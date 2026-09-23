"""Optional backend tests in its pinned environment, separate from core tests."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from research.chemistry.reaction_probe import run_probe


class ReactionChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report=run_probe()

    def test_elements(self):
        self.assertLess(self.report['checks']['element_mass_fraction_max_abs_error'],1e-8)

    def test_energy(self):
        self.assertLess(self.report['checks']['adiabatic_enthalpy_max_relative_error'],1e-7)

    def test_constraints_differ(self):
        initial=self.report['initial']
        tp=self.report['equilibrium']['TP']
        hp=self.report['equilibrium']['HP']
        self.assertAlmostEqual(tp['temperature_k'],initial['temperature_k'],places=6)
        self.assertGreater(hp['temperature_k'],tp['temperature_k'])

    def test_kinetics_not_initial_state(self):
        series=self.report['kinetic_series']
        self.assertEqual(len(series),11)
        self.assertTrue(all(a['time_s']<b['time_s'] for a,b in zip(series,series[1:])))
        self.assertGreater(series[-1]['mass_fractions']['H2O'],series[0]['mass_fractions']['H2O'])

    def test_replay(self):
        repeated=run_probe()
        self.assertEqual(self.report['mechanism_sha256'],repeated['mechanism_sha256'])
        self.assertAlmostEqual(self.report['equilibrium']['HP']['temperature_k'],repeated['equilibrium']['HP']['temperature_k'],places=8)

    def test_archive_integrity(self):
        manifest=json.loads((ROOT/'data/manifests/reaction-heat-acquisition-2026-09-23.json').read_text())
        for record in manifest['records']:
            path=ROOT/record['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record['sha256'])
            if path.suffix in ('.zip','.whl'):
                with zipfile.ZipFile(path) as archive:
                    self.assertIsNone(archive.testzip())


if __name__=='__main__': unittest.main()
