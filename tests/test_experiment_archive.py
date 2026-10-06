"""Tests for immutable observed-outcome report storage."""

import tempfile
import unittest
from pathlib import Path

from research.chemistry.foundation import digest
from research.process.experiment_archive import (
    ExperimentArchiveError,
    load_experiment_validation,
    save_experiment_validation,
)


def _report() -> dict:
    report = {
        "schema_version": "experiment-validation-v1",
        "input_hash": "placeholder",
        "status": "PARTIAL",
        "comparisons": {},
        "warnings": [],
        "limitations": [],
    }
    report["input_hash"] = digest({"experiment": "archive-test"})
    return report


class ExperimentArchiveTests(unittest.TestCase):
    def test_save_is_idempotent_and_load_verifies_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = _report()
            created = save_experiment_validation(report, root)
            existing = save_experiment_validation(report, root)
            loaded = load_experiment_validation(report["input_hash"], root)

            self.assertEqual(created["status"], "CREATED")
            self.assertEqual(existing["status"], "EXISTS")
            self.assertEqual(loaded["status"], "AVAILABLE")
            self.assertEqual(loaded["report"], report)

    def test_same_id_with_changed_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = _report()
            save_experiment_validation(report, root)
            changed = dict(report, warnings=["changed"])

            with self.assertRaises(ExperimentArchiveError) as context:
                save_experiment_validation(changed, root)

            self.assertEqual(str(context.exception), "EXPERIMENT_RUN_ID_CONFLICT")


if __name__ == "__main__":
    unittest.main()
