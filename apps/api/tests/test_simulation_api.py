"""API contract tests for target-driven, material-agnostic scenarios."""
import copy
import unittest

from fastapi.testclient import TestClient

from apps.api.app.main import app


def payload():
    return {
        "scenario_id": "api-generic-001",
        "body": {
            "layer_id": "body",
            "materials": [{"analysis_id": "body/porcelain-001", "role": "BODY", "amount_g": 1000}],
        },
        "layers": [
            {
                "layer_id": "engobe",
                "materials": [{"analysis_id": "engobe/iron-001", "role": "ENGOBE"}],
                "application_method": "DIP",
                "coat_count": 1,
                "dry_thickness_um": 200,
            },
            {
                "layer_id": "glaze",
                "materials": [
                    {"analysis_id": "glaze/base-001", "role": "GLAZE"},
                    {"analysis_id": "oxide/copper-001", "role": "ADDITION", "amount_g": 4},
                ],
                "application_method": "BRUSH",
                "coat_count": 3,
            },
        ],
        "final_firing": {
            "name": "custom-research-cycle",
            "start_c": 20,
            "segments": [
                {"target_c": 600, "rate_c_per_hour": 100, "hold_minutes": 10},
                {"target_c": 1220, "rate_c_per_hour": 120, "hold_minutes": 15},
            ],
            "atmosphere": "OXIDATION",
        },
        "geometry": {"kind": "TILE", "thickness_mm": 8, "length_mm": 100, "width_mm": 100},
        "target": {
            "objective": "Compare fit and firing timeline",
            "requested_outputs": ["oxide_composition", "firing_timeline", "fit_risk", "melt_fraction"],
        },
        "property_inventory": {
            "body/porcelain-001": ["oxide_analysis", "cte"],
            "engobe/iron-001": ["oxide_analysis"],
            "glaze/base-001": ["oxide_analysis", "cte"],
            "oxide/copper-001": ["oxide_analysis"],
        },
    }


class SimulationAPITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_accepts_arbitrary_layers_and_returns_explicit_statuses(self):
        response = self.client.post('/api/v1/simulations/capabilities', json=payload())
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['schema_version'], 'simulation-capabilities-v1')
        self.assertEqual(result['outputs']['oxide_composition']['status'], 'AVAILABLE')
        self.assertEqual(result['outputs']['firing_timeline']['status'], 'AVAILABLE')
        self.assertEqual(result['outputs']['fit_risk']['status'], 'PARTIAL')
        self.assertEqual(result['outputs']['melt_fraction']['status'], 'UNAVAILABLE')

    def test_same_snapshot_replays_same_hash(self):
        request = payload()
        first = self.client.post('/api/v1/simulations/capabilities', json=request).json()
        second = self.client.post('/api/v1/simulations/capabilities', json=request).json()
        self.assertEqual(first['input_hash'], second['input_hash'])

    def test_duplicate_layer_is_rejected(self):
        request = payload()
        request['layers'].append(copy.deepcopy(request['layers'][0]))
        response = self.client.post('/api/v1/simulations/capabilities', json=request)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['errors'][0]['code'], 'INVALID_SIMULATION_SCENARIO')

    def test_bad_request_is_rejected_by_schema(self):
        request = payload()
        request['body']['materials'][0]['amount_g'] = -1
        response = self.client.post('/api/v1/simulations/capabilities', json=request)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['errors'][0]['code'], 'INVALID_INPUT')


if __name__ == '__main__':
    unittest.main()
