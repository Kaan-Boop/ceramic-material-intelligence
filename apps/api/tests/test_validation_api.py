import unittest
from fastapi.testclient import TestClient
from apps.api.app.main import app
from research.process.validation import CONTEXT

class ValidationApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        base = dict(context={k:'demo' for k in CONTEXT}, source_ref='fixture',
                    method_version='v1',data_kind='SYNTHETIC',temperature_basis='SPECIMEN',unit='degC')
        self.payload = dict(prediction=dict(base,evidence_kind='PREDICTED',samples=[dict(time_s=0,temperature_c=22)]),
                            observation=dict(base,evidence_kind='OBSERVED',samples=[dict(time_s=0,temperature_c=20)]))

    def test_compare(self):
        r=self.client.post('/api/v1/validation/temperature',json=self.payload)
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['metrics']['mae_C'],2)
        self.assertEqual(r.headers['cache-control'],'no-store')

    def test_kiln_not_specimen(self):
        self.payload['observation']['temperature_basis']='PROGRAMMED_KILN'
        r=self.client.post('/api/v1/validation/temperature',json=self.payload)
        self.assertEqual(r.status_code,422)

    def test_missing_fields(self):
        self.payload['prediction']={}
        self.assertEqual(self.client.post('/api/v1/validation/temperature',json=self.payload).status_code,422)

    def test_health_probe(self):
        r = self.client.get('/api/v1/health')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'ok')
        self.assertEqual(r.json()['service'], 'ceramic-api')
