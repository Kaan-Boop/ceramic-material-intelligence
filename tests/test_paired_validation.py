from copy import deepcopy
import unittest
from research.process.validation import compare_temperature, CONTEXT
from research.process.outcomes import OutcomeInputError


class PairedValidationTests(unittest.TestCase):
    def setUp(self):
        self.p = dict(context={k: 'synthetic-'+k for k in CONTEXT},
                      source_ref='synthetic-fixture', method_version='fixture-v1',
                      evidence_kind='PREDICTED', data_kind='SYNTHETIC',
                      temperature_basis='SPECIMEN', unit='degC',
                      samples=[{'time_s':0,'temperature_c':22},{'time_s':10,'temperature_c':96}])
        self.o = deepcopy(self.p)
        self.o['evidence_kind']='OBSERVED'
        self.o['samples']=[{'time_s':0,'temperature_c':20},{'time_s':10,'temperature_c':100}]

    def test_hand_calculation(self):
        r=compare_temperature(self.p,self.o)
        self.assertEqual(r['metrics']['bias_C'],-1)
        self.assertEqual(r['metrics']['mae_C'],3)
        self.assertAlmostEqual(r['metrics']['rmse_C'],10**.5)
        self.assertEqual(r['independent_specimen_count'],1)
        self.assertEqual(r['qualifier'],'SYNTHETIC_CHECK')
        self.assertEqual(r['acceptance_status'],'NOT_ASSESSED')

    def test_mismatches_rejected(self):
        for key,value in [('unit','K'),('temperature_basis','PROGRAMMED_KILN'),('data_kind','REAL')]:
            o=deepcopy(self.o); o[key]=value
            with self.assertRaises(OutcomeInputError): compare_temperature(self.p,o)
        o=deepcopy(self.o); o['context']['glaze_revision']='different'
        with self.assertRaises(OutcomeInputError): compare_temperature(self.p,o)

    def test_time_alignment(self):
        self.o['samples'][1]['time_s']=11
        with self.assertRaises(OutcomeInputError): compare_temperature(self.p,self.o)

    def test_nonfinite_rejected(self):
        for v in [float('nan'), float('inf'), True, 10**1000]:
            self.p['samples'][0]['temperature_c']=v
            with self.assertRaises(OutcomeInputError): compare_temperature(self.p,self.o)

    def test_snapshot_and_replay(self):
        r=compare_temperature(self.p,self.o)
        self.assertEqual(r,compare_temperature(self.p,self.o))
        self.p['samples'][0]['temperature_c']=50
        self.assertEqual(r['input_snapshot']['prediction']['samples'][0]['temperature_c'],22)
