import math
import unittest
from research.process.reference_viscosity import viscosity, reference_flow, MATERIAL_ID
from research.process.outcomes import OutcomeInputError


class ReferenceViscosityTests(unittest.TestCase):
    def test_certificate_combined_table_rounding(self):
        # Page 1 Table 1 last column, not independent experimental observations.
        for log_poise, t in [(2, 1434.3), (3, 1181.7), (4, 1019.0), (5, 905.3), (6, 821.5)]:
            actual = math.log10(viscosity(t, MATERIAL_ID)['viscosity_pa_s']) + 1
            self.assertLess(abs(actual-log_poise), .001)

    def test_poise_to_pas(self):
        t = 266 + 4236.118 / (3 + 1.626)
        self.assertAlmostEqual(viscosity(t, MATERIAL_ID)['viscosity_pa_s'], 100)

    def test_decreases_with_temperature(self):
        self.assertGreater(viscosity(900, MATERIAL_ID)['viscosity_pa_s'],
                           viscosity(1200, MATERIAL_ID)['viscosity_pa_s'])

    def test_no_other_material(self):
        with self.assertRaises(OutcomeInputError): viscosity(1200, 'generic-stoneware-glaze')

    def test_no_extrapolation_or_invalid_number(self):
        for t in [800, 1500, True, None, float('nan'), float('inf'), 10**400]:
            with self.assertRaises(OutcomeInputError): viscosity(t, MATERIAL_ID)

    def scenario(self, **changes):
        args = dict(temperature_c=1200, material_id=MATERIAL_ID, density_kg_m3=2500,
                    density_source_ref='fixture:synthetic-density-not-NIST', density_input_kind='SYNTHETIC',
                    thickness_mm=.5, inclination_deg=90, duration_s=60, ideal_film_assumptions=True)
        args.update(changes)
        return reference_flow(**args)

    def test_bridge_hand_calculation_and_scope(self):
        r = self.scenario()
        eta = viscosity(1200, MATERIAL_ID)['viscosity_pa_s']
        expected = 2500 * 9.80665 * .0005**2 / (3*eta) * 60 * 1000
        self.assertAlmostEqual(r['values']['ideal_mean_travel_mm'], expected)
        self.assertEqual(r['qualifier'], 'SYNTHETIC_SCENARIO')
        self.assertIsNone(r['probability'])

    def test_required_assumptions_and_provenance(self):
        for changes in [dict(ideal_film_assumptions=False), dict(density_source_ref=''),
                        dict(density_input_kind='UNKNOWN'), dict(density_kg_m3=-1)]:
            with self.assertRaises(OutcomeInputError): self.scenario(**changes)

    def test_scaling_and_replay(self):
        r = self.scenario()
        self.assertEqual(r, self.scenario())
        self.assertAlmostEqual(self.scenario(duration_s=120)['values']['ideal_mean_travel_mm'],
                               2*r['values']['ideal_mean_travel_mm'])

    def test_source_uncertainty_not_fake_confidence(self):
        r = viscosity(1200, MATERIAL_ID)
        self.assertIsNone(r['uncertainty'])
        self.assertIn('0.020', r['source_equation_annotation'])
