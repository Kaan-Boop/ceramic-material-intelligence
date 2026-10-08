import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from apps.api.app.main import app


class LabMeasurementAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = self.temp.name
        self.env = patch.dict(os.environ, {
            "EXPERIMENT_RECORD_ROOT": f"{root}/records",
            "EXPERIMENT_MEASUREMENT_ROOT": f"{root}/measurements",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.client = TestClient(app)

    def create_record(self, kind="REAL"):
        response = self.client.post("/api/v1/experiments", json={
            "experiment_id": "exp-lab-01",
            "specimen_id": "tile-01",
            "record_kind": kind,
            "source_ref": "lab:session-01",
            "context": {
                "body_revision": "body-1",
                "glaze_revision": "glaze-1",
                "application_revision": "apply-1",
                "firing_run_id": "kiln-run-1",
            },
        })
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["record_id"]

    def test_real_measurement_round_trip(self):
        record_id = self.create_record()
        payload = {
            "observable": "glaze_runout_distance_mm",
            "value": 4.2,
            "unit": "mm",
            "specimen_id": "tile-01",
            "source_ref": "lab:session-01",
            "method": "edge reference to final glaze boundary",
            "status": "MEASURED",
            "conditions": {"surface_angle_deg": 90},
        }
        response = self.client.post(f"/api/v1/experiments/{record_id}/measurements", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["measurement"]["evidence_kind"], "OBSERVED")
        repeated = self.client.post(f"/api/v1/experiments/{record_id}/measurements", json=payload)
        self.assertEqual(repeated.status_code, 200, repeated.text)
        self.assertEqual(repeated.json()['status'], 'EXISTS')
        self.assertEqual(repeated.json()['measurement'], response.json()['measurement'])
        listed = self.client.get(f"/api/v1/experiments/{record_id}/measurements")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)

    def test_synthetic_record_cannot_receive_empirical_measurement(self):
        record_id = self.create_record(kind="SYNTHETIC")
        payload = {
            "observable": "glaze_surface_class", "value": "MATTE", "unit": None,
            "specimen_id": "tile-01", "source_ref": "lab:session-01",
            "method": "visual assessment", "status": "OBSERVED",
        }
        response = self.client.post(f"/api/v1/experiments/{record_id}/measurements", json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["errors"][0]["code"], "MEASUREMENT_REQUIRES_REAL_EXPERIMENT")

    def test_bad_unit_is_rejected(self):
        record_id = self.create_record()
        payload = {
            "observable": "glaze_runout_distance_mm", "value": 4.2, "unit": "%",
            "specimen_id": "tile-01", "source_ref": "lab:session-01",
            "method": "edge reference", "status": "MEASURED",
        }
        response = self.client.post(f"/api/v1/experiments/{record_id}/measurements", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["errors"][0]["code"], "UNIT_MISMATCH")

    def test_measurement_must_match_record_specimen(self):
        record_id = self.create_record()
        payload = {
            "observable": "firing_linear_shrinkage_pct", "value": 7.4, "unit": "%",
            "specimen_id": "different-tile", "source_ref": "lab:session-01",
            "method": "marked axis", "status": "MEASURED",
        }
        response = self.client.post(f"/api/v1/experiments/{record_id}/measurements", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["errors"][0]["code"], "SPECIMEN_ID_MISMATCH")

    def test_invalid_record_id_is_a_controlled_error(self):
        response = self.client.get("/api/v1/experiments/not-a-record/measurements")
        self.assertEqual(response.status_code, 422)

    def test_numbers_are_not_coerced_from_strings_or_booleans(self):
        record_id = self.create_record()
        for value in [True, '7.4']:
            payload = {
                'observable':'firing_linear_shrinkage_pct', 'value':value, 'unit':'%',
                'specimen_id':'tile-01', 'source_ref':'lab:session-01', 'method':'marked axis', 'status':'MEASURED',
            }
            response = self.client.post(f'/api/v1/experiments/{record_id}/measurements', json=payload)
            self.assertEqual(response.status_code, 422, response.text)

    def test_openapi_declares_typed_measurement_and_archive(self):
        schemas = app.openapi()['components']['schemas']
        self.assertIn('LabMeasurementArchiveResponse', schemas)
        self.assertIn('optical_transmission_class', schemas['LabMeasurementRequest']['properties']['observable']['enum'])


if __name__ == "__main__":
    unittest.main()
