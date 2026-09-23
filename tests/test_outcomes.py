import json
from copy import deepcopy
from pathlib import Path
import unittest
from research.process.outcomes import assess_outcomes, OutcomeInputError

FIXTURE = Path(__file__).resolve().parents[1]/'data/fixtures/outcome-indicators-synthetic.json'


class OutcomeTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text())

    def report(self):
        return assess_outcomes(self.data)['sections']

    def test_fit_hand_calculation(self):
        r = self.report()['fit']['values']
        self.assertAlmostEqual(r['free_contraction_difference_microstrain'], 960)
        self.assertEqual(r['nominal_direction'], 'TENSILE_TENDENCY')

    def test_fit_reverse_and_zero(self):
        self.data['fit']['glaze_mean_cte_per_k'] = 4e-6
        self.assertEqual(self.report()['fit']['values']['nominal_direction'], 'COMPRESSIVE_TENDENCY')
        self.data['fit']['glaze_mean_cte_per_k'] = 6e-6
        self.assertEqual(self.report()['fit']['values']['nominal_direction'], 'ZERO_NOMINAL_MISMATCH')

    def test_flow_hand_calculation(self):
        self.assertAlmostEqual(self.report()['flow']['values']['ideal_mean_travel_mm'], 1.22583125)

    def test_flow_thickness_squared(self):
        a = self.report()['flow']['values']['ideal_mean_travel_mm']
        self.data['flow']['thickness_mm'] *= 2
        self.assertAlmostEqual(self.report()['flow']['values']['ideal_mean_travel_mm'], 4*a)

    def test_horizontal_no_gravity_flow(self):
        self.data['flow']['inclination_deg'] = 0
        self.assertEqual(self.report()['flow']['values']['ideal_mean_travel_mm'], 0)

    def test_wetting_hand_calculation(self):
        self.assertAlmostEqual(self.report()['wetting']['values']['ideal_work_of_adhesion_j_m2'], .45)

    def test_porosity_distinct_quantities(self):
        r = self.report()['porosity']['values']
        self.assertAlmostEqual(r['water_absorption_mass_pct'], 2)
        self.assertAlmostEqual(r['apparent_open_porosity_volume_pct'], 100*2/42)

    def test_gloss_spread_not_probability(self):
        r = self.report()['gloss']
        self.assertEqual(r['values']['mean_gu'], 30)
        self.assertEqual(r['values']['sample_sd_gu'], 2)
        self.assertIsNone(r['probability'])

    def test_single_gloss_no_fake_sd(self):
        self.data['gloss']['readings_gu'] = [30]
        self.assertIsNone(self.report()['gloss']['values']['sample_sd_gu'])

    def test_missing_all_unavailable(self):
        self.assertTrue(all(s['status']=='UNAVAILABLE' for s in assess_outcomes({})['sections'].values()))

    def test_invalid_and_assumptions(self):
        changes = [('fit','same_interval_and_cooling_basis',False), ('fit','high_c',10),
                   ('flow','viscosity_pa_s',0), ('flow','ideal_film_assumptions',False),
                   ('wetting','contact_angle_deg',181), ('porosity','suspended_mass_g',102),
                   ('gloss','angle_deg',30), ('flow','source_ref',''),
                   ('fit','body_mean_cte_per_k',True), ('flow','temperature_c',float('nan'))]
        for section, field, value in changes:
            data = deepcopy(self.data)
            data[section][field] = value
            with self.subTest(field=field), self.assertRaises(OutcomeInputError):
                assess_outcomes(data)

    def test_rejects_noncreeping_flow(self):
        self.data['flow']['viscosity_pa_s'] = .001
        with self.assertRaises(OutcomeInputError): self.report()

    def test_unknown_fields(self):
        self.data['flow']['secret_default'] = 10
        with self.assertRaises(OutcomeInputError): self.report()
        with self.assertRaises(OutcomeInputError): assess_outcomes({'made_up': {}})

    def test_replay_no_mutation_and_provenance(self):
        before = deepcopy(self.data)
        a = assess_outcomes(self.data)
        self.assertEqual(a, assess_outcomes(self.data))
        self.assertEqual(self.data, before)
        self.data['flow']['source_ref'] = 'different-source'
        self.assertNotEqual(a['input_hash'], assess_outcomes(self.data)['input_hash'])


if __name__ == '__main__': unittest.main()
