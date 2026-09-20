import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pipelines.ingestion.reference_certificates import number, validate, REVIEWED
from pipelines.ingestion.inventory import build_inventory

ROOT = Path(__file__).resolve().parents[1]


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "data/reference/nist-certified-elements-v1.json").read_text(encoding="utf-8"))

    def test_transcribed_counts_and_units(self):
        self.assertEqual(sum(len(r["measurements"]) for r in self.document["records"]), 39)
        self.assertEqual(self.document["records"][0]["measurements"][1], ["Ca", "0.1770", "0.0051", "wt_pct", "2.5"])
        self.assertEqual(self.document["records"][3]["measurements"][4], ["Fe", "278.7", "8.0", "mg/kg", "2"])
        self.assertIsNone(self.document["records"][1]["measurements"][0][4])

    def test_no_implicit_basis_or_analysis_date(self):
        self.assertEqual(self.document["records"][3]["analysis_basis"], "UNKNOWN")
        self.assertTrue(all(r["analysis_date"] is None for r in self.document["records"]))

    def test_invalid_numbers(self):
        for value in (True, None, 1.2, "NaN", "Infinity", "-1", "<1", "1,2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                number(value)

    def test_scope_guard(self):
        self.document["core_engine_eligible"] = True
        with self.assertRaisesRegex(ValueError, "REFERENCE_SCOPE_REQUIRED"):
            validate(self.document, ROOT, {})

    def fixture(self, root):
        """Synthetic raw fixtures; never assert these are actual certificate bytes."""
        source = {"source_license": self.document["source_license"], "license_evidence": self.document["license_evidence"],
                  "commercial_use_allowed": "ALLOWED", "rights_partition": "NIST_NON_SRD_REFERENCE"}
        receipt = {"sources": {"nist-srm-ceramics": source}, "failures": {}, "files": []}
        reviewed = {}
        for record in self.document["records"]:
            slug, _, count = REVIEWED[record["product_code"]]
            content = f"SYNTHETIC TEST {slug}".encode()
            digest = hashlib.sha256(content).hexdigest()
            (root / digest).write_bytes(content)
            record["raw_sha256"] = digest
            reviewed[record["product_code"]] = (slug, digest, count)
            receipt["files"].append({"source_id": "nist-srm-ceramics", "sha256": digest,
                                     "raw_path": digest, "source_url": record["source_url"]})
        return receipt, reviewed

    def run_fixture(self, mutation=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, reviewed = self.fixture(root)
            if mutation:
                mutation(self.document, receipt, root)
            with patch("pipelines.ingestion.reference_certificates.REVIEWED", reviewed):
                return validate(self.document, root, receipt)

    def test_valid_reference(self):
        self.assertEqual(self.run_fixture()["certified_element_values"], 39)

    def test_corruption(self):
        def corrupt(doc, receipt, root):
            (root / receipt["files"][0]["raw_path"]).write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "CERTIFICATE_HASH_MISMATCH"):
            self.run_fixture(corrupt)

    def test_dry_clay_not_k2(self):
        def change(doc, receipt, root):
            doc["records"][1]["measurements"][0][4] = "2"
        with self.assertRaisesRegex(ValueError, "TOLERANCE_IS_NOT_EXPANDED_UNCERTAINTY"):
            self.run_fixture(change)

    def test_bad_unit(self):
        def change(doc, receipt, root):
            doc["records"][0]["measurements"][0][3] = "mol_pct"
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_UNIT"):
            self.run_fixture(change)

    def test_duplicate_element(self):
        def change(doc, receipt, root):
            doc["records"][0]["measurements"][1][0] = "Al"
        with self.assertRaisesRegex(ValueError, "INVALID_OR_DUPLICATE_ELEMENT"):
            self.run_fixture(change)

    def test_partial_receipt_not_accepted(self):
        def change(doc, receipt, root):
            receipt["failures"]["nist-srm-ceramics"] = "incomplete"
        with self.assertRaisesRegex(ValueError, "UNREVIEWED_REFERENCE_RIGHTS"):
            self.run_fixture(change)

    def test_inventory_retains_custom_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "receipts").mkdir()
            (root / "profile").mkdir()
            (root / "profile/report.json").write_text("{}", encoding="utf-8")
            source = {"license": self.document["source_license"], "commercial_use_allowed": "ALLOWED",
                      "rights_partition": "NIST_NON_SRD_REFERENCE", "license_conditions": "retain NIST conditions",
                      "license_evidence": self.document["license_evidence"]}
            receipt = {"sources": {"nist-srm-ceramics": source}, "created_at": "2026-09-20", "failures": {}, "files": []}
            (root / "receipts/fixture.json").write_text(json.dumps(receipt), encoding="utf-8")
            actual = build_inventory(root, root / "profile")["sources"]["nist-srm-ceramics"]
            self.assertEqual(actual, source)


if __name__ == "__main__":
    unittest.main()
