import json
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
from apps.api.app.main import app
from research.process.outcomes import assess_outcomes


class OutcomeAPITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.data = json.loads((Path(__file__).resolve().parents[3]/'data/fixtures/outcome-indicators-synthetic.json').read_text())

    def test_matches_engine(self):
        r = self.client.post('/api/v1/outcomes/assess', json=self.data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), assess_outcomes(self.data))
        self.assertEqual(r.headers['cache-control'], 'no-store')

    def test_invalid(self):
        self.data['flow']['viscosity_pa_s'] = '1000'
        self.assertEqual(self.client.post('/api/v1/outcomes/assess', json=self.data).status_code, 422)

    def test_empty_no_prediction(self):
        r = self.client.post('/api/v1/outcomes/assess', json={})
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.json()['overall_success_probability'])

    def test_unknown_section(self):
        self.assertEqual(self.client.post('/api/v1/outcomes/assess', json={'unknown': {}}).status_code, 422)
