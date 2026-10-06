import tempfile
import unittest
from pathlib import Path

from research.process.experiment_record import (
    ExperimentRecordError,
    build_record,
    load_experiment_record,
    save_experiment_record,
)


class ExperimentRecordTests(unittest.TestCase):
    def payload(self):
        return {
            "experiment_id": "cone6-white-01",
            "specimen_id": "tile-01-a",
            "record_kind": "REAL",
            "question": "Bu sır bünyede nasıl davranıyor?",
            "source_ref": "lab:notebook:2026-10-06",
            "context": {
                "body_revision": "body:white-stoneware:v1",
                "glaze_revision": "glaze:test:v1",
                "application_revision": "application:dip-2-coats",
                "firing_run_id": "kiln:2026-10-06-01",
            },
            "analysis_report_id": "report-abc",
            "chemistry_input_hash": "hash-abc",
            "notes": "Bağımsız ölçüm daha sonra eklenecek.",
        }

    def test_build_marks_missing_context_without_filling_it(self):
        payload = self.payload()
        payload["context"]["firing_run_id"] = ""
        record = build_record(payload)
        self.assertEqual(record["missing_context"], ["firing_run_id"])
        self.assertEqual(record["context"]["firing_run_id"], "")

    def test_save_is_idempotent_and_load_verifies_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            record = build_record(self.payload())
            first = save_experiment_record(record, directory)
            second = save_experiment_record(record, directory)
            loaded = load_experiment_record(record["record_id"], directory)
            self.assertEqual(first["status"], "CREATED")
            self.assertEqual(second["status"], "EXISTS")
            self.assertEqual(loaded["record"]["record_id"], record["record_id"])

    def test_invalid_record_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ExperimentRecordError):
                save_experiment_record({"schema_version": "wrong", "record_id": "x"}, Path(directory))
