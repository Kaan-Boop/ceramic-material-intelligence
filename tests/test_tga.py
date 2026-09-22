import copy
import unittest
from research.thermal.tga import analyze_trace, replay_water


class TgaTests(unittest.TestCase):
    def setUp(self):
        self.trace = dict(source_ref='synthetic:test-v1', sample_id='synthetic-10mg',
                          atmosphere='synthetic-air', mass_basis='ABSOLUTE_SAMPLE_MASS_MG',
                          data_kind='SYNTHETIC', samples=[[0, 25, 10], [10, 50, 9], [30, 100, 8]])
        self.alloc = [dict(water_fraction=.5, kind='SCENARIO_ASSUMPTION', source_ref='synthetic:allocation') for _ in range(2)]
        self.chamber = dict(volume_m3=1., flow_m3_s=0., initial_kg_m3=0., inlet_kg_m3=0.,
                            saturation_kg_m3=.02, temperature_c=25, source_ref='synthetic:chamber')

    def test_units_and_irregular_time(self):
        r = analyze_trace(self.trace)
        self.assertAlmostEqual(r['net_mass_loss_kg'], 2e-6)
        self.assertAlmostEqual(r['intervals'][0]['interval_average_net_loss_kg_s'], 1e-7)
        self.assertAlmostEqual(r['intervals'][1]['interval_average_net_loss_kg_s'], 5e-8)

    def test_conservation(self):
        r = analyze_trace(self.trace)
        self.assertAlmostEqual(sum(i['interval_average_net_loss_kg_s']*i['duration_s'] for i in r['intervals']), r['net_mass_loss_kg'])

    def test_gain_preserved_and_replay_blocked(self):
        self.trace['samples'][1][2] = 11
        r = analyze_trace(self.trace)
        self.assertAlmostEqual(r['mass_gain_kg'], 1e-6)
        with self.assertRaisesRegex(ValueError, 'MASS_GAIN'):
            replay_water(self.trace, self.alloc, self.chamber)

    def test_unknown_gas_not_water(self):
        self.assertEqual(analyze_trace(self.trace)['intervals'][0]['gas_identity'], 'UNKNOWN')
        with self.assertRaises(ValueError):
            replay_water(self.trace, [], self.chamber)

    def test_integrated_water_budget(self):
        r = replay_water(self.trace, self.alloc, self.chamber)
        self.assertAlmostEqual(r['final_vapor_kg_m3'], 1e-6)
        self.assertTrue(all(abs(x['result']['mass_balance_residual_kg']) < 1e-18 for x in r['segments']))

    def test_saturation_stops_remaining_segments(self):
        self.chamber['saturation_kg_m3'] = 1e-8
        r = replay_water(self.trace, self.alloc, self.chamber)
        self.assertEqual(r['status'], 'UNAVAILABLE')
        self.assertEqual(r['unprocessed_intervals'], 1)
        self.assertIsNone(r['final_vapor_kg_m3'])

    def test_snapshot_and_reproducibility(self):
        r = replay_water(self.trace, self.alloc, self.chamber)
        self.assertEqual(r, replay_water(**r['input_snapshot']))
        self.trace['samples'][0][2] = 100
        self.assertEqual(r['input_snapshot']['trace']['samples'][0][2], 10)

    def test_invalid_time_mass_temperature(self):
        for point in ([0, 30, 9], [5, -273.15, 9], [5, 30, -1], [5, 30, float('nan')], [True, 30, 9]):
            t = copy.deepcopy(self.trace)
            t['samples'][1] = point
            with self.subTest(point=point), self.assertRaises(ValueError):
                analyze_trace(t)

    def test_metadata_required(self):
        for key in ('source_ref', 'sample_id', 'atmosphere', 'mass_basis', 'data_kind'):
            t = copy.deepcopy(self.trace)
            del t[key]
            with self.assertRaises(ValueError):
                analyze_trace(t)

    def test_no_qualitative_ms_as_quantitative_fraction(self):
        for update in ({'kind': 'QUALITATIVE_MS'}, {'water_fraction': 1.1}, {'source_ref': ''}):
            a = copy.deepcopy(self.alloc)
            a[0].update(update)
            with self.assertRaises(ValueError):
                replay_water(self.trace, a, self.chamber)
