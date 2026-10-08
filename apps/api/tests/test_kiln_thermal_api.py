"""Local thermal solver endpoint; numerical estimates, never observed results."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from fastapi.testclient import TestClient
from apps.api.app.main import app
from research.thermal.kiln_1d import simulate

FIXTURE = Path(__file__).resolve().parents[3] / "data/fixtures/kiln-thermal-1d-synthetic.json"


class KilnThermalAPITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.case = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.case["schedule"]["points"] = [{"time_s": 0, "gas_c": 20, "wall_c": 20},
                                           {"time_s": 60, "gas_c": 100, "wall_c": 110}]

    def test_api_matches_core_and_preserves_provenance(self):
        response = self.client.post('/api/v1/simulations/thermal-1d', json={"case": self.case})
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result, simulate(self.case))
        self.assertEqual(result["evidence_kind"], "PREDICTED")
        self.assertEqual(result["physical_validation"], "NOT_PERFORMED")
        self.assertIsNone(result["uncertainty"])
        self.assertEqual(result["unavailable_sections"]["melt_fraction"], "NO_PHASE_MODEL")

    def test_invalid_cases_have_stable_codes(self):
        cases = []
        missing = deepcopy(self.case); del missing["layers"][0]["density_kg_m3"]
        cases.append((missing, "INVALID_FIELDS"))
        domain = deepcopy(self.case); domain["layers"][0]["valid_temperature_c"] = [0, 10]
        cases.append((domain, "OUT_OF_MATERIAL_DOMAIN"))
        oversized = deepcopy(self.case); oversized["max_step_s"] = 1e-6
        cases.append((oversized, "SIMULATION_SIZE_LIMIT"))
        bad_type = deepcopy(self.case); bad_type["layers"][0]["conductivity_w_m_k"] = "1.2"
        cases.append((bad_type, "INVALID_NUMBER"))
        for case, expected in cases:
            with self.subTest(code=expected):
                response = self.client.post('/api/v1/simulations/thermal-1d', json={"case": case})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["errors"][0]["code"], expected)

    def test_extra_top_level_fields_and_nonlocal_origin_rejected(self):
        self.assertEqual(self.client.post('/api/v1/simulations/thermal-1d', json={"case": self.case, "save": True}).status_code, 422)
        response = self.client.post('/api/v1/simulations/thermal-1d', json={"case": self.case}, headers={"Origin": "https://example.invalid"})
        self.assertEqual(response.status_code, 403)

    def test_openapi_exposes_case_contract(self):
        schema = self.client.get('/openapi.json').json()
        self.assertIn('/api/v1/simulations/thermal-1d', schema["paths"])
        self.assertEqual(schema["components"]["schemas"]["KilnThermalRequest"]["required"], ["case"])

    def test_comparison_endpoint_retains_physical_validation_boundary(self):
        from research.thermal.validation import evaluate
        request = json.loads(FIXTURE.with_name('kiln-thermal-comparison-synthetic.json').read_text(encoding='utf-8'))
        response = self.client.post('/api/v1/simulations/thermal-1d/compare', json={'experiment': request})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), evaluate(request))
        self.assertEqual(response.json()['physical_validation'], 'NOT_ESTABLISHED')
        self.assertEqual(response.json()['observed_real_specimen_count'], 0)
        request['observation']['record']['data_kind'] = 'REAL'
        rejected = self.client.post('/api/v1/simulations/thermal-1d/compare', json={'experiment': request})
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(rejected.json()['errors'][0]['code'], 'REAL_SYNTHETIC_MISMATCH')


if __name__ == "__main__":
    unittest.main()
