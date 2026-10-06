import tempfile
import unittest

from research.process.experiment_observation import (
    build_observation,
    list_observations,
    load_observation,
    save_observation,
)
from research.process.experiment_record import build_record


class ExperimentObservationTests(unittest.TestCase):
    def setUp(self):
        self.record = build_record({
            "experiment_id": "exp-1", "specimen_id": "spec-1", "record_kind": "REAL",
            "source_ref": "lab:test", "context": {},
        })
        self.payload = {
            "observable": "water_absorption_mass_pct", "value": 10.0, "unit": "%",
            "specimen_id": "spec-1", "source_ref": "lab:test", "method": "ASTM C373",
            "status": "MEASURED",
        }

    def test_save_is_idempotent_and_lists_by_record(self):
        observation = build_observation(self.record["record_id"], self.payload)
        with tempfile.TemporaryDirectory() as directory:
            first = save_observation(observation, directory)
            second = save_observation(observation, directory)
            loaded = load_observation(observation["observation_id"], directory)
            rows = list_observations(self.record["record_id"], directory)
            self.assertEqual(first["status"], "CREATED")
            self.assertEqual(second["status"], "EXISTS")
            self.assertEqual(loaded["observation"]["observation_id"], observation["observation_id"])
            self.assertEqual(len(rows), 1)

    def test_observation_keeps_reported_status(self):
        payload = dict(self.payload, status="REPORTED")
        observation = build_observation(self.record["record_id"], payload)
        self.assertEqual(observation["observation"]["status"], "REPORTED")
