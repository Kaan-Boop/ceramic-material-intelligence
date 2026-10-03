from io import BytesIO
import hashlib
import unittest
import warnings
import zipfile

from pipelines.ingestion.acquire import Collector
from pipelines.ingestion.melt_evidence import (
    SUPPLEMENT, ZENODO_FILES, ZENODO_RECORD, selected_pdf_from_zip,
    validate_zenodo_record, checked_zenodo_file,
)


def bundle(names):
    stream = BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(stream, "w") as archive:
            for name, data in names:
                archive.writestr(name, data)
    return stream.getvalue()


def record():
    return {"id": ZENODO_RECORD, "metadata": {"doi": f"10.5281/zenodo.{ZENODO_RECORD}",
            "access_right": "open", "license": {"id": "cc-by-4.0"}},
            "files": [{"key": name, "size": 100,
                       "links": {"self": f"https://zenodo.org/api/records/{ZENODO_RECORD}/files/{name}/content"}}
                      for name in ZENODO_FILES]}


class MeltEvidenceTests(unittest.TestCase):
    def test_only_expected_pdf_selected(self):
        raw = bundle([(SUPPLEMENT, b"%PDF-test"), ("other.gif", b"unselected")])
        pdf, members = selected_pdf_from_zip(raw)
        self.assertEqual(pdf, b"%PDF-test")
        self.assertEqual(sum(m["selected"] for m in members), 1)

    def test_zip_traversal_absolute_and_windows_paths_rejected(self):
        for name in ("../bad", "/bad", "C:/bad", "..\\bad"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "UNSAFE"):
                selected_pdf_from_zip(bundle([(SUPPLEMENT, b"%PDF-ok"), (name, b"x")]))

    def test_duplicate_pdf_rejected(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            selected_pdf_from_zip(bundle([(SUPPLEMENT, b"%PDF-a"), (SUPPLEMENT, b"%PDF-b")]))

    def test_missing_and_invalid_pdf(self):
        with self.assertRaisesRegex(ValueError, "MISSING"):
            selected_pdf_from_zip(bundle([("other.pdf", b"%PDF-x")]))
        with self.assertRaisesRegex(ValueError, "NOT_PDF"):
            selected_pdf_from_zip(bundle([(SUPPLEMENT, b"<html>error</html>")]))

    def test_zenodo_identity_and_license(self):
        self.assertEqual(len(validate_zenodo_record(record())), 6)
        data = record()
        data["id"] += 1
        with self.assertRaisesRegex(ValueError, "VERSION"):
            validate_zenodo_record(data)
        data = record()
        data["metadata"]["license"]["id"] = "cc-by-nc-4.0"
        with self.assertRaisesRegex(ValueError, "RIGHTS"):
            validate_zenodo_record(data)

    def test_missing_duplicate_and_redirected_files(self):
        data = record()
        data["files"].pop()
        with self.assertRaisesRegex(ValueError, "SELECTION"):
            validate_zenodo_record(data)
        data = record()
        data["files"].append(data["files"][0])
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            validate_zenodo_record(data)
        data = record()
        data["files"][0]["links"]["self"] = "https://example.com/wrong"
        with self.assertRaisesRegex(ValueError, "URL"):
            validate_zenodo_record(data)

    def test_checksum_and_size(self):
        raw = b"content"
        info = {"size": len(raw), "checksum": "md5:" + hashlib.md5(raw).hexdigest()}
        checked_zenodo_file(raw, info)
        with self.assertRaisesRegex(ValueError, "SIZE"):
            checked_zenodo_file(b"x", info)
        with self.assertRaisesRegex(ValueError, "CHECKSUM"):
            checked_zenodo_file(b"changed", info)

    def test_file_and_transport_size_bounds_before_network(self):
        data = record()
        data["files"][0]["size"] = 20 * 1024 * 1024
        with self.assertRaisesRegex(ValueError, "SIZE"):
            validate_zenodo_record(data)
        for cap in (0, -1, True, 33 * 1024 * 1024):
            with self.subTest(cap=cap), self.assertRaisesRegex(ValueError, "SIZE"):
                Collector("unused").fetch("https://www.ebi.ac.uk/example", max_bytes=cap)


if __name__ == "__main__":
    unittest.main()
