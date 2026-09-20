"""Intake safety/quality tests; these do not validate a chemistry engine."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipelines.ingestion import materials as m
from pipelines.ingestion.acquire import checked_url

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/fixtures/synthetic-materials.json"
RIGHTS = ROOT / "data/fixtures/synthetic-rights.json"


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.data = m.read_json(FIXTURE)
        self.rights = m.read_json(RIGHTS)

    def run_intake(self):
        return m.analyze(self.data, self.rights, "INTERNAL_VALIDATION")

    def codes(self):
        return {i["code"] for d in self.run_intake()["dispositions"] for i in d["issues"]}

    def test_valid_synthetic(self):
        result = self.run_intake()
        self.assertEqual(result["counts"]["accepted"], 3)
        self.assertEqual([r["basis_balance_total"] for r in result["normalized"]], [100, 100, 100])

    def test_never_mutates_input(self):
        before = copy.deepcopy(self.data)
        self.run_intake()
        self.assertEqual(before, self.data)

    def test_missing_basis(self):
        self.data["records"][0]["analysis_basis"] = "UNKNOWN"
        self.assertIn("ANALYSIS_BASIS_UNKNOWN", self.codes())

    def test_negative_percentage_rejected(self):
        self.data["records"][0]["oxides"] = {"SiO2": -1}
        self.assertEqual(self.run_intake()["counts"]["rejected"], 1)

    def test_unsupported_oxide_preserved(self):
        self.data["records"][0]["oxides"] = {"FeO": 100}
        self.assertIn("UNSUPPORTED_OXIDE", self.codes())
        self.assertEqual(self.data["records"][0]["oxides"], {"FeO": 100})

    def test_trace_not_zero(self):
        self.data["records"][0]["oxides"] = {"SiO2": "<0.01"}
        self.assertIn("UNSUPPORTED_VALUE_FORMAT", self.codes())

    def test_boolean_not_numeric(self):
        self.data["records"][0]["oxides"] = {"SiO2": True}
        self.assertIn("UNSUPPORTED_VALUE_FORMAT", self.codes())

    def test_huge_integer_controlled(self):
        self.data["records"][0]["oxides"] = {"SiO2": 10**400}
        self.assertIn("UNSUPPORTED_VALUE_FORMAT", self.codes())

    def test_duplicate_json_keys(self):
        with self.assertRaisesRegex(m.IntakeError, "DUPLICATE_JSON_KEY"):
            m.load_json_bytes(b'{"a":1,"a":2}')

    def test_nonfinite_json(self):
        for value in (b'NaN', b'Infinity', b'1e999'):
            with self.subTest(value=value), self.assertRaises(m.IntakeError):
                m.load_json_bytes(b'{"x":' + value + b'}')

    def test_totals_not_silently_closed(self):
        self.data["records"][0]["oxides"]["SiO2"] = 98
        self.assertIn("ANALYSIS_TOTAL_REVIEW", self.codes())
        self.assertEqual(self.data["records"][0]["oxides"]["SiO2"], 98)

    def test_mass_gain_quarantines_not_rejects(self):
        self.data["records"][0]["loi_pct"] = -0.1
        self.assertIn("UNSUPPORTED_MASS_CHANGE_MODEL", self.codes())
        self.assertEqual(self.run_intake()["counts"]["rejected"], 0)

    def test_as_received_moisture_not_counted_twice(self):
        record = self.data["records"][1]
        record.update(analysis_basis="AS_RECEIVED", loi_reference_basis="AS_RECEIVED",
                      loi_includes_moisture=True, moisture_pct=2, moisture_reference_basis="AS_RECEIVED")
        self.assertEqual(self.run_intake()["counts"]["accepted"], 3)

    def test_loi_basis_required(self):
        del self.data["records"][1]["loi_reference_basis"]
        self.assertIn("LOI_BASIS_UNRESOLVED", self.codes())

    def test_incomplete_chemistry(self):
        self.data["records"][0]["coverage"] = "PARTIAL"
        self.assertIn("INCOMPLETE_CHEMISTRY", self.codes())

    def test_missing_source(self):
        self.data["records"][0]["source_id"] = "missing"
        with self.assertRaisesRegex(m.IntakeError, "UNRESOLVED_RECORD_SOURCE"):
            self.run_intake()

    def test_unhashable_source_controlled(self):
        self.data["records"][0]["source_id"] = []
        with self.assertRaises(m.IntakeError):
            self.run_intake()

    def test_rights_cannot_be_self_granted(self):
        self.data["sources"]["project-synthetic"]["store"] = "ALLOWED"
        self.rights["sources"]["project-synthetic"]["store"] = "UNKNOWN"
        with self.assertRaisesRegex(m.IntakeError, "RAW_STORAGE_NOT_ALLOWED"):
            self.run_intake()

    def test_rights_purpose_requires_list(self):
        self.rights["sources"]["project-synthetic"]["purposes"] = "INTERNAL_VALIDATION"
        with self.assertRaisesRegex(m.IntakeError, "INVALID_RIGHTS_LEDGER"):
            self.run_intake()

    def test_synthetic_never_reference(self):
        result = m.analyze(self.data, self.rights, "INTERNAL_REFERENCE")
        self.assertEqual(result["counts"]["accepted"], 0)

    def test_reported_record_requires_exact_review(self):
        record = self.data["records"][0]
        record["record_kind"] = "REPORTED"
        self.assertIn("RECORD_REVIEW_REQUIRED", self.codes())
        self.rights["sources"]["project-synthetic"]["approved_analysis_hashes"] = [m.digest(record)]
        self.assertEqual(self.run_intake()["counts"]["accepted"], 3)
        record["material_name"] = "changed"
        self.assertIn("RECORD_REVIEW_REQUIRED", self.codes())

    def test_batch_duplicates(self):
        self.data["records"].append(copy.deepcopy(self.data["records"][0]))
        result = self.run_intake()
        self.assertEqual(result["counts"]["duplicate_skipped"], 1)
        self.assertEqual(result["counts"]["accepted"], 3)

    def test_rights_revision_rechecks(self):
        seen = [d["decision_key"] for d in self.run_intake()["dispositions"]]
        self.rights["sources"]["project-synthetic"]["decision_version"] = "2"
        self.assertEqual(m.analyze(self.data, self.rights, "INTERNAL_VALIDATION", seen)["counts"]["duplicate_skipped"], 0)

    def test_import_replay_preserves_raw_and_skips_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            first = m.import_file(FIXTURE, RIGHTS, temp, "INTERNAL_VALIDATION")
            second = m.import_file(FIXTURE, RIGHTS, temp, "INTERNAL_VALIDATION")
            self.assertEqual(first["counts"]["accepted"], 3)
            self.assertEqual(second["counts"]["duplicate_skipped"], 3)
            self.assertEqual((Path(temp)/"runs"/first["run_id"]/"raw/source.json").read_bytes(), FIXTURE.read_bytes())

    def test_corrupt_previous_run_stops_import(self):
        with tempfile.TemporaryDirectory() as temp:
            report = m.import_file(FIXTURE, RIGHTS, temp, "INTERNAL_VALIDATION")
            path = Path(temp)/"runs"/report["run_id"]/"raw/source.json"
            path.write_bytes(b'{}')
            with self.assertRaisesRegex(m.IntakeError, "CHECKSUM_MISMATCH"):
                m.import_file(FIXTURE, RIGHTS, temp, "INTERNAL_VALIDATION")

    def test_locked_import_does_not_remove_other_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            lock = Path(temp)/".import.lock"
            lock.touch()
            with self.assertRaisesRegex(m.IntakeError, "IMPORT_LOCKED"):
                m.import_file(FIXTURE, RIGHTS, temp, "INTERNAL_VALIDATION")
            self.assertTrue(lock.exists())

    def test_failed_publish_leaves_no_committed_run(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(m.os, "replace", side_effect=OSError("test")):
            with self.assertRaises(OSError):
                m.import_file(FIXTURE, RIGHTS, temp, "INTERNAL_VALIDATION")
            self.assertEqual(list((Path(temp)/"runs").iterdir()), [])
            self.assertFalse((Path(temp)/".import.lock").exists())
            self.assertEqual(list(Path(temp).glob(".pending-*")), [])

    def test_unreviewed_download_host_rejected(self):
        for url in ("http://zenodo.org/file", "https://example.com/file", "https://user@zenodo.org/file"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                checked_url(url)


if __name__ == "__main__":
    unittest.main()
