"""Run with unittest discover -s apps/api/tests in the prototype environment."""
import unittest
from copy import deepcopy

from fastapi.testclient import TestClient
from apps.api.app.main import app
from research.chemistry.recipe_demo import demo
from research.chemistry.recipe import analyze_recipe


class PrototypeAPITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.example = self.client.get('/api/v1/materials').json()['example']

    def test_matches_engine_and_replays(self):
        response = self.client.post('/api/v1/analyses', json=self.example)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        expected = analyze_recipe(self.example['ingredients'], demo()['input_snapshot']['analyses'], base_mass_g=self.example['base_mass_g'])
        self.assertEqual(result['chemistry'], expected)
        self.assertEqual(result['chemistry']['oxide_mass_g'], demo()['oxide_mass_g'])
        self.assertEqual(result, self.client.post('/api/v1/analyses', json=self.example).json())
        self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_context_does_not_change_chemistry(self):
        first = self.client.post('/api/v1/analyses', json=self.example).json()
        self.example['context']['cone'] = '10'
        second = self.client.post('/api/v1/analyses', json=self.example).json()
        self.assertEqual(first['chemistry'], second['chemistry'])
        self.assertNotEqual(first['report_id'], second['report_id'])

    def test_invalid_amounts_and_unknowns(self):
        for value in [-1, True, '40', None, 1e7, 1e-300]:
            request = deepcopy(self.example)
            request['ingredients'][0]['amount'] = value
            self.assertEqual(self.client.post('/api/v1/analyses', json=request).status_code, 422)
        self.example['ingredients'][0]['analysis_id'] = 'generic-feldspar'
        self.assertEqual(self.client.post('/api/v1/analyses', json=self.example).json()['errors'][0]['code'], 'UNKNOWN_ANALYSIS')

    def test_nonfinite_rejected_without_echo(self):
        response = self.client.post('/api/v1/analyses', content='{"base_mass_g": NaN}', headers={'content-type': 'application/json'})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn('NaN', response.text)

    def test_zero_base_and_no_flux(self):
        for r in self.example['ingredients']:
            r['amount'] = 0
        self.assertEqual(self.client.post('/api/v1/analyses', json=self.example).json()['errors'][0]['code'], 'ZERO_BASE_TOTAL')
        self.example['ingredients'] = [{'analysis_id': 'pure_silica', 'amount': 100, 'role': 'BASE'}]
        result = self.client.post('/api/v1/analyses', json=self.example).json()['chemistry']
        self.assertEqual(result['umf']['status'], 'UNAVAILABLE')
        self.assertIsNone(result['ratios']['SiO2_to_Al2O3_molar']['value'])

    def test_addition_base_and_mass(self):
        self.example['ingredients'].append({'analysis_id': 'pure_silica', 'amount': 2, 'role': 'ADDITION'})
        result = self.client.post('/api/v1/analyses', json=self.example).json()['chemistry']
        self.assertEqual(result['total_dry_batch_mass_g'], 102)
        self.assertAlmostEqual(result['retained_oxide_mass_g'] + result['loi_mass_g'], 102)

    def test_request_limits_and_origin(self):
        self.example['ingredients'] *= 26
        self.assertEqual(self.client.post('/api/v1/analyses', json=self.example).status_code, 422)
        self.assertEqual(self.client.post('/api/v1/analyses', content='x' * 65537).status_code, 413)
        self.assertEqual(self.client.post('/api/v1/analyses', json={}, headers={'origin':'https://untrusted.example'}).status_code, 403)

    def test_catalogue_is_explicitly_theoretical(self):
        rows = self.client.get('/api/v1/materials').json()['materials']
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r['qualifier'] == 'THEORETICAL_NOT_MANUFACTURER_ANALYSIS' for r in rows))

    def test_process_report_without_fake_probabilities(self):
        result = self.client.post('/api/v1/analyses', json=self.example).json()['process']
        self.assertEqual(len(result['stages']), 6)
        self.assertTrue(all(s['probability'] is None for s in result['stages']))

    def test_process_schedule_and_window(self):
        self.example['context'].update(temperature_c=1230, body_window=dict(
            product_id='synthetic-test-only', min_c=1200, max_c=1280,
            source_ref='synthetic-fixture', conditions='Not a commercial product'),
            schedule=dict(start_c=30,segments=[dict(target_c=1230,rate_c_per_hour=100,hold_minutes=20)]))
        response = self.client.post('/api/v1/analyses', json=self.example)
        self.assertEqual(response.status_code, 200)
        result = response.json()['process']
        self.assertEqual(result['schedule']['total_duration_minutes'],740)
        self.assertEqual(result['body_window']['code'],'WITHIN_REPORTED_WINDOW')
        self.example['context']['body_window']['min_c'] = 1500
        self.assertEqual(self.client.post('/api/v1/analyses',json=self.example).status_code,422)


if __name__ == '__main__':
    unittest.main()
