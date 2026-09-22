import math
import unittest
from research.thermal.vapor import chamber_segment


class VaporTests(unittest.TestCase):
    def run_case(self, **kwargs):
        inputs = dict(volume_m3=1., flow_m3_s=.01, duration_s=100., initial_kg_m3=0.,
                      inlet_kg_m3=0., source_kg_s=.00001, saturation_kg_m3=.02,
                      source_ref='synthetic:benchmark-v1')
        return chamber_segment(**(inputs | kwargs))

    def test_closed_accumulation(self):
        r = self.run_case(flow_m3_s=0)
        self.assertAlmostEqual(r['final_vapor_kg_m3'], .001)
        self.assertEqual(r['diagnostic_mass_budget_kg']['outlet'], 0)

    def test_hand_analytical_solution(self):
        r = self.run_case()
        self.assertAlmostEqual(r['final_vapor_kg_m3'], .001*(1-math.exp(-1)))
        self.assertAlmostEqual(r['mass_balance_residual_kg'], 0, places=15)

    def test_purge(self):
        r = self.run_case(source_kg_s=0, initial_kg_m3=.01)
        self.assertAlmostEqual(r['final_vapor_kg_m3'], .01*math.exp(-1))

    def test_steady_inlet(self):
        r = self.run_case(source_kg_s=0, initial_kg_m3=.003, inlet_kg_m3=.003)
        self.assertAlmostEqual(r['final_vapor_kg_m3'], .003)

    def test_step_partition_invariance(self):
        half = self.run_case(duration_s=50)
        second = self.run_case(duration_s=50, initial_kg_m3=half['final_vapor_kg_m3'])
        self.assertAlmostEqual(second['final_vapor_kg_m3'], self.run_case()['final_vapor_kg_m3'])

    def test_tiny_flow(self):
        r = self.run_case(flow_m3_s=1e-20)
        self.assertAlmostEqual(r['final_vapor_kg_m3'], .001)
        self.assertAlmostEqual(r['mass_balance_residual_kg'], 0)

    def test_saturation_stops_prediction(self):
        r = self.run_case(source_kg_s=.1)
        self.assertEqual(r['status'], 'UNAVAILABLE')
        self.assertIsNone(r['final_vapor_kg_m3'])
        self.assertIsNone(r['defect_probability'])

    def test_invalid(self):
        for kw in ({'volume_m3': 0}, {'flow_m3_s': -1}, {'duration_s': float('nan')},
                   {'source_kg_s': True}, {'source_ref': ''}, {'initial_kg_m3': .03}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.run_case(**kw)

    def test_zero_time(self):
        self.assertEqual(self.run_case(duration_s=0, initial_kg_m3=.005)['final_vapor_kg_m3'], .005)
