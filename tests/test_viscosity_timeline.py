import unittest
from research.process.viscosity_timeline import evaluate
from research.process.reference_viscosity import MATERIAL_ID, viscosity
from research.process.outcomes import OutcomeInputError


class ViscosityTimelineTests(unittest.TestCase):
    def run_case(self, **changes):
        args = dict(material_id=MATERIAL_ID, source_ref='fixture:synthetic-cycle',
                    temperature_basis='SYNTHETIC', samples=[
                        dict(time_s=0, temperature_c=20), dict(time_s=600, temperature_c=1100),
                        dict(time_s=1200, temperature_c=1200), dict(time_s=1800, temperature_c=20)])
        args.update(changes)
        return evaluate(**args)

    def test_partial_never_zero_fills(self):
        r = self.run_case()
        self.assertEqual(r['status'], 'PARTIAL')
        self.assertEqual(r['available_sample_count'], 2)
        self.assertIsNone(r['series'][0]['viscosity_pa_s'])
        self.assertEqual(r['series'][2]['viscosity_pa_s'], viscosity(1200, MATERIAL_ID)['viscosity_pa_s'])

    def test_program_is_not_specimen(self):
        r = self.run_case(temperature_basis='PROGRAMMED_KILN')
        self.assertEqual(r['status'], 'UNAVAILABLE')
        self.assertTrue(all(x['reason']=='SPECIMEN_TEMPERATURE_REQUIRED' for x in r['series']))

    def test_all_available(self):
        self.assertEqual(self.run_case(samples=[dict(time_s=0, temperature_c=1200)])['status'], 'AVAILABLE')

    def test_invalid_samples(self):
        for samples in [[], [dict(time_s=0, temperature_c=10**400)],
                        [dict(time_s=0, temperature_c=1000)]*2,
                        [dict(time_s=True, temperature_c=1000)],
                        [dict(time_s=0, temperature_c=float('nan'))],
                        [dict(time_s=0, temperature_c=1000, extra=1)]]:
            with self.assertRaises(OutcomeInputError): self.run_case(samples=samples)

    def test_invalid_metadata(self):
        for change in [dict(source_ref=''), dict(material_id='clay'), dict(temperature_basis='UNKNOWN')]:
            with self.assertRaises(OutcomeInputError): self.run_case(**change)

    def test_replay_and_input_isolation(self):
        samples = [dict(time_s=0, temperature_c=1000)]
        a = self.run_case(samples=samples)
        self.assertEqual(a, self.run_case(samples=samples))
        a['input_snapshot']['samples'][0]['temperature_c'] = 1100
        self.assertEqual(samples[0]['temperature_c'], 1000)

    def test_lineage_changes_hash(self):
        self.assertNotEqual(self.run_case()['input_hash'], self.run_case(source_ref='different')['input_hash'])

    def test_no_fake_uncertainty(self):
        r = self.run_case()
        self.assertIsNone(r['uncertainty'])
        self.assertEqual(r['qualifier'], 'SYNTHETIC_SCENARIO')
