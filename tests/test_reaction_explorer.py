import unittest
from research.chemistry.reaction_explorer import explore
from research.chemistry.foundation import ChemistryInputError

class ReactionExplorerTests(unittest.TestCase):
    def test_endpoints(self):
        self.assertEqual(explore(100,0)['current']['CaCO3_g'],100)
        r=explore(100,1)
        self.assertTrue(r['balance']['balanced'])
        self.assertEqual(r['current']['CaCO3_g'],0)
        self.assertAlmostEqual(r['current']['CO2_g'],43.97,places=1)
        self.assertAlmostEqual(r['mass_residual_g'],0,places=10)
    def test_curve_and_scale(self):
        a,b=explore(100,.5),explore(200,.5)
        self.assertEqual(len(a['series']),21)
        self.assertAlmostEqual(b['current']['CaO_g'],2*a['current']['CaO_g'])
        for row in a['series']:
            self.assertAlmostEqual(sum(row[k] for k in ('CaCO3_g','CaO_g','CO2_g')),100)
        self.assertEqual(a['conversion_from_temperature']['status'],'UNAVAILABLE')
    def test_bad_inputs(self):
        for mass,x in [(0,0),(100,-1),(100,1.1),(True,0),(100,float('nan')),(10**1000,0)]:
            with self.assertRaises(ChemistryInputError): explore(mass,x)
    def test_repeatable(self):
        self.assertEqual(explore(100,.4),explore(100,.4))
