import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipelines.ingestion.chemistry_sources import acquire, SOURCES


def fake_fetch(self, url):
    for source in SOURCES:
        if source["repository"] in url and url.endswith("/" + source["license_file"]):
            return source["marker"].encode(), url
    return b"# inert test reference\n", url


class ChemistrySourceTests(unittest.TestCase):
    def test_receipt_integrity_and_replay(self):
        with tempfile.TemporaryDirectory() as root, patch("pipelines.ingestion.chemistry_sources.Collector.fetch", fake_fetch):
            first = acquire(root)
            second = acquire(root)
            self.assertEqual(first["source_count"], 3)
            self.assertEqual(first["file_count"], 15)
            self.assertEqual(first["production_material_analyses_added"], 0)
            self.assertTrue(all(f["reused"] for f in second["files"]))
            for f in first["files"]:
                self.assertEqual(hashlib.sha256((Path(root) / f["raw_path"]).read_bytes()).hexdigest(), f["sha256"])
                self.assertEqual((Path(root) / f["raw_path"]).read_bytes(), (Path(root) / f["readable_path"]).read_bytes())

    def test_license_drift_rejected(self):
        with tempfile.TemporaryDirectory() as root, patch("pipelines.ingestion.chemistry_sources.Collector.fetch", return_value=(b"unknown terms", "https://raw.githubusercontent.com/")):
            with self.assertRaisesRegex(ValueError, "LICENSE_REVIEW_REQUIRED"):
                acquire(root)

    def test_corrupt_readable_archive_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root, patch("pipelines.ingestion.chemistry_sources.Collector.fetch", fake_fetch):
            first = acquire(root)
            path = Path(root) / first["files"][0]["readable_path"]
            path.write_bytes(b"corrupt fixture")
            with self.assertRaisesRegex(ValueError, "IMMUTABLE_SOURCE_CONFLICT"):
                acquire(root)
            self.assertEqual(path.read_bytes(), b"corrupt fixture")

    def test_network_failure_not_success(self):
        with tempfile.TemporaryDirectory() as root, patch("pipelines.ingestion.chemistry_sources.Collector.fetch", side_effect=OSError("offline")):
            with self.assertRaises(OSError):
                acquire(root)

    def test_no_external_material_files_or_autoexecution(self):
        for source in SOURCES:
            self.assertEqual(len(source["commit"]), 40)
            self.assertIn(source["license_file"], source["files"])
            self.assertFalse(any("materials.json" in filename or filename.endswith(".pth") for filename in source["files"]))
