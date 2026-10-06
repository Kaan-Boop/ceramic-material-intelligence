"""Tests for immutable local comparison-run storage."""

import tempfile
import unittest
from pathlib import Path

from research.external.comparison import compare_calculated_reports
from research.external.comparison_archive import (
    ComparisonArchiveError,
    load_comparison_snapshot,
    save_comparison_snapshot,
)


def _snapshot() -> dict:
    internal = {
        "input_hash": "internal-hash",
        "engine_version": "engine/1",
        "umf_convention": "standard-flux-v1",
        "umf": {"values": {"SiO2": 3.0}},
        "ratios": {"SiO2_to_Al2O3_molar": {"value": 6.0}},
    }
    external = {
        "source": "OpenGlaze",
        "report": {
            "success": True,
            "missing_materials": [],
            "umf_formula": {"SiO2": 3.2},
            "ratios": {"sio2_al2o3": 6.4},
        },
    }
    return compare_calculated_reports(
        internal,
        external,
        external_ingredients=[{"name": "Silica", "amount": 100}],
        cone=6,
    )


class ComparisonArchiveTests(unittest.TestCase):
    def test_save_is_idempotent_and_load_replays(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = _snapshot()

            created = save_comparison_snapshot(snapshot, root)
            existing = save_comparison_snapshot(snapshot, root)
            loaded = load_comparison_snapshot(snapshot["input_hash"], root)

            self.assertEqual(created["status"], "CREATED")
            self.assertEqual(existing["status"], "EXISTS")
            self.assertEqual(loaded["status"], "AVAILABLE")
            self.assertEqual(loaded["replay"]["status"], "PASS")
            self.assertEqual(loaded["snapshot"], snapshot)

    def test_same_id_with_changed_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = _snapshot()
            save_comparison_snapshot(snapshot, root)
            changed = dict(snapshot)
            changed["warnings"] = ["değiştirildi"]

            with self.assertRaises(ComparisonArchiveError) as context:
                save_comparison_snapshot(changed, root)

            self.assertEqual(str(context.exception), "COMPARISON_ID_CONFLICT")

    def test_tampered_archive_fails_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = _snapshot()
            save_comparison_snapshot(snapshot, root)
            archive_path = root / f"{snapshot['input_hash']}.json"
            archive_path.write_text(archive_path.read_text(encoding="utf-8").replace("OpenGlaze", "Changed"), encoding="utf-8")

            with self.assertRaises(ComparisonArchiveError) as context:
                load_comparison_snapshot(snapshot["input_hash"], root)

            self.assertEqual(str(context.exception), "ARCHIVE_CHECKSUM_MISMATCH")


if __name__ == "__main__":
    unittest.main()
