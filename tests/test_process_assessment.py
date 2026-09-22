import unittest
from copy import deepcopy
from research.process.assessment import assess_process, firing_window, schedule_duration, ProcessInputError


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.window = dict(min_c=1200, max_c=1280, product_id='synthetic-only', source_ref='synthetic-fixture', conditions='Synthetic test range; not a product')

    def test_window_boundaries(self):
        for t, code in [(1199,'BELOW_REPORTED_WINDOW'),(1200,'WITHIN_REPORTED_WINDOW'),(1280,'WITHIN_REPORTED_WINDOW'),(1281,'ABOVE_REPORTED_WINDOW')]:
            self.assertEqual(firing_window(self.window,t)['code'],code)

    def test_unknown_is_not_within(self):
        self.assertEqual(firing_window(None,1230)['status'],'UNAVAILABLE')
        self.assertEqual(firing_window(self.window,None)['code'],'NO_PEAK_TEMPERATURE')

    def test_window_validation(self):
        for patch in [dict(min_c=1400),dict(source_ref=''),dict(conditions=''),dict(min_c=True),dict(max_c=float('nan'))]:
            with self.assertRaises(ProcessInputError):
                firing_window(self.window | patch,1230)

    def test_ramp_hold_and_cooling(self):
        plan = dict(start_c=20, segments=[dict(target_c=620,rate_c_per_hour=100,hold_minutes=20),dict(target_c=20,rate_c_per_hour=200)])
        self.assertEqual(schedule_duration(plan)['total_duration_minutes'],560)
        self.assertEqual(schedule_duration(plan)['peak_c'],620)

    def test_natural_cooling_is_partial(self):
        r = schedule_duration(dict(start_c=20,segments=[dict(target_c=620,rate_c_per_hour=100),dict(target_c=20,rate_c_per_hour=None)]))
        self.assertEqual(r['known_duration_minutes'],360)
        self.assertIsNone(r['total_duration_minutes'])
        self.assertEqual(r['status'],'PARTIAL')

    def test_invalid_rates_and_natural_heating(self):
        for rate in [0,-1,True,float('inf'),None]:
            with self.assertRaises(ProcessInputError):
                schedule_duration(dict(start_c=20,segments=[dict(target_c=100,rate_c_per_hour=rate)]))

    def test_no_predictions_even_with_ranges(self):
        r = assess_process(dict(temperature_c=1230,body_window=self.window,glaze_window=self.window))
        self.assertTrue(all(s['probability'] is None and s['status']=='UNAVAILABLE' for s in r['stages']))
        self.assertEqual(r['body_window']['code'],'WITHIN_REPORTED_WINDOW')

    def test_replay_and_no_mutation(self):
        c = dict(temperature_c=1230,body_window=self.window)
        original=deepcopy(c)
        r=assess_process(c)
        self.assertEqual(c,original)
        self.assertEqual(r,assess_process(c))
        c['temperature_c']=1250
        self.assertNotEqual(r['input_hash'],assess_process(c)['input_hash'])

    def test_mismatch_not_silently_corrected(self):
        r=assess_process(dict(temperature_c=1230,schedule=dict(start_c=20,segments=[dict(target_c=1250,rate_c_per_hour=100)])))
        self.assertTrue(any('farklı' in w for w in r['warnings']))
        self.assertEqual(r['input_snapshot']['temperature_c'],1230)

    def test_no_cone_conversion(self):
        r=assess_process(dict(cone='6'))
        self.assertIsNone(r['schedule']['peak_c'])
        self.assertEqual(r['body_window']['status'],'UNAVAILABLE')
