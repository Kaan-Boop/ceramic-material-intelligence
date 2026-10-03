import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ScheeliteStagingTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / 'data/reference' / name).read_text(encoding='utf-8'))

    def test_recipes_are_complete_nominal_batches(self):
        data = self.load('scheelite-recipes-staging.json')
        self.assertEqual(len(data['rows']), 8)
        self.assertEqual(len({r['sample'] for r in data['rows']}), 8)
        for row in data['rows']:
            self.assertEqual(len(row['amounts']), len(data['ingredient_order']))
            self.assertAlmostEqual(sum(row['amounts']), 100)

    def test_unverified_data_cannot_be_mistaken_for_approved(self):
        for name in ['scheelite-recipes-staging.json', 'scheelite-outcomes-staging.json']:
            data = self.load(name)
            self.assertFalse(data['engine_eligible'])
            self.assertFalse(data['training_allowed'])
            self.assertEqual(data['status'], 'STAGING_NOT_VALIDATED')

    def test_outcome_links_to_recipe_and_keeps_unknowns(self):
        recipes = self.load('scheelite-recipes-staging.json')
        data = self.load('scheelite-outcomes-staging.json')
        for row in data['observations']:
            self.assertIn(row['sample'], {r['sample'] for r in recipes['rows']})
            self.assertIsNone(row['uncertainty'])
            self.assertIsNone(row['actual_specimen_temperature_C'])
            self.assertEqual(row['figure_crosscheck'], 'PENDING')

    def test_archived_source_hash(self):
        data = self.load('scheelite-outcomes-staging.json')
        path = ROOT / 'storage/research/literature-2026-09-27/fulltext-pilot' / (data['raw_sha256'] + '.xml')
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), data['raw_sha256'])
