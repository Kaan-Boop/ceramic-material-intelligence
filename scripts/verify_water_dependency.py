"""Installation/consistency checks, explicitly not independent EOS validation."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from research.thermal.water import pure_water


class WaterChecks(unittest.TestCase):
    def test_liquid(self):
        result=pure_water(300,101325)
        self.assertEqual(result['phase'],'liquid')
        self.assertTrue(990 < result['values']['density_kg_m3'] < 1005)

    def test_vapor(self):
        result=pure_water(400,101325)
        self.assertEqual(result['phase'],'gas')
        self.assertTrue(0.4 < result['values']['density_kg_m3'] < 0.7)

    def test_enthalpy_identity(self):
        for temperature in (300,400):
            result=pure_water(temperature,101325)['values']
            residual=result['enthalpy_j_kg']-result['internal_energy_j_kg']-101325/result['density_kg_m3']
            self.assertLess(abs(residual),0.01)

    def test_invalid(self):
        for temp,press in [(True,101325),(float('nan'),101325),(1500,101325),(300,-1),(300,float('inf'))]:
            with self.assertRaises(ValueError): pure_water(temp,press)

    def test_repeatable(self):
        self.assertEqual(pure_water(300,101325),pure_water(300,101325))


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(WaterChecks))
    if not result.wasSuccessful():
        sys.exit(1)
    manifest=json.loads((ROOT/'data/manifests/engine-dependencies-2026-09-23.json').read_text())
    for record in manifest['records']:
        assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256']
    payload={'tests_run':result.testsRun,'status':'PASS','archived_file_hashes_verified':len(manifest['records']),
             'validation_level':'INSTALLATION_AND_INTERNAL_CONSISTENCY_NOT_INDEPENDENT_PHYSICAL_VALIDATION',
             'cases':[pure_water(300,101325),pure_water(400,101325)]}
    output=ROOT/'data/manifests/water-dependency-check-2026-09-23.json'
    output.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    print(output)
