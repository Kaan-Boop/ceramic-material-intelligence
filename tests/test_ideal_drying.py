import unittest
from research.thermal.drying import simulate


class IdealDryingTests(unittest.TestCase):
    def run_case(self, **changes):
        # Synthetic constants, independent analytic solution: C=1400 J/K,
        # warmup=112000 J, latent inventory=200000 J; not real water data.
        args = dict(dry_mass_kg=1, water_mass_kg=.1, solid_cp_j_kg_k=1000,
                    initial_temperature_k=293.15, net_power_w=1000,
                    times_s=[0, 56, 112, 212, 312, 400],
                    properties=dict(saturation_temperature_k=373.15,
                                    liquid_enthalpy=lambda t: 4000*(t-293.15),
                                    liquid_enthalpy_j_kg=320000,
                                    vapor_enthalpy_j_kg=2320000, method='SYNTHETIC'))
        args.update(changes)
        return simulate(**args)

    def test_analytic_warmup(self):
        r = self.run_case()
        self.assertAlmostEqual(r['warmup_energy_j'], 112000)
        self.assertAlmostEqual(r['series'][1]['temperature_k'], 333.15)

    def test_half_evaporated(self):
        s = self.run_case()['series'][3]
        self.assertAlmostEqual(s['remaining_water_kg'], .05)
        self.assertAlmostEqual(s['temperature_k'], 373.15)

    def test_exhaustion_and_unused_energy(self):
        s = self.run_case()['series'][-1]
        self.assertEqual(s['stage'], 'WATER_EXHAUSTED_MODEL_END')
        self.assertAlmostEqual(s['outside_model_energy_j'], 88000)
        self.assertEqual(s['remaining_water_kg'], 0)

    def test_conservation(self):
        for s in self.run_case()['series']:
            self.assertAlmostEqual(s['remaining_water_kg']+s['emitted_water_kg'], .1)
            self.assertAlmostEqual(s['energy_residual_j'], 0, places=6)

    def test_zero_power(self):
        for s in self.run_case(net_power_w=0)['series']:
            self.assertAlmostEqual(s['temperature_k'], 293.15)
            self.assertEqual(s['emitted_water_kg'], 0)

    def test_invalid_inputs(self):
        for change in [dict(water_mass_kg=-1), dict(dry_mass_kg=True),
                       dict(net_power_w=float('nan')), dict(times_s=[0, 2, 1]),
                       dict(times_s=[]), dict(initial_temperature_k=400)]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_case(**change)

    def test_grid_independence(self):
        self.assertEqual(self.run_case()['series'][-1],
                         self.run_case(times_s=[0,400])['series'][-1])

    def test_scaling(self):
        a = self.run_case()['series'][3]
        b = self.run_case(dry_mass_kg=2, water_mass_kg=.2, net_power_w=2000)['series'][3]
        self.assertAlmostEqual(a['temperature_k'], b['temperature_k'])
        self.assertAlmostEqual(a['emitted_water_kg']*2, b['emitted_water_kg'])


if __name__ == '__main__':
    unittest.main()
