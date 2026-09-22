import json
import unittest
from copy import deepcopy
from research.commercial_catalogue import SEED, build, audit


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.seed=json.loads(SEED.read_text(encoding='utf-8'))
        self.rows=build(self.seed)

    def test_no_unknown_chemistry_admitted(self):
        self.assertTrue(all(not r['chemistry_engine_eligible'] and r['oxide_analysis'] is None and r['ingredient_recipe'] is None for r in self.rows))

    def test_identity_and_sources(self):
        report=audit(self.rows)
        self.assertEqual(report['duplicate_ids'],0)
        self.assertEqual(report['source_url_missing'],0)
        self.assertEqual(report['unknown_reuse_rights'],len(self.rows))

    def test_repeatable(self):
        self.assertEqual(self.rows,build(self.seed))

    def test_duplicate_source_does_not_inflate(self):
        seed=deepcopy(self.seed)
        seed['groups'].append(deepcopy(seed['groups'][0]))
        with self.assertRaises(ValueError):
            build(seed)

    def test_manufacture_and_market_separate(self):
        imported=[r for r in self.rows if r['brand']=='Laguna' and r['discovery_market']=='TR']
        self.assertTrue(imported)
        self.assertTrue(all(r['manufacturing_country'] is None for r in imported))

    def test_sds_not_formula(self):
        rows=[r for r in self.rows if r['source_type']=='MANUFACTURER_GROUP_SDS']
        self.assertTrue(rows)
        self.assertTrue(all('SDS_IS_NOT_FULL_FORMULA' in r['quality_flags'] and r['oxide_analysis'] is None for r in rows))

    def test_targets_not_reported_complete(self):
        self.assertFalse(audit(self.rows)['target_completed'])

    def test_candidate_lineage_and_quarantine(self):
        payload=json.loads((SEED.parent/'commercial-analysis-candidates.json').read_text(encoding='utf-8'))
        source_ids={r['source_id'] for r in self.rows}
        self.assertEqual(payload['layer'],'QUARANTINE_NOT_ENGINE_INPUT')
        for row in payload['records']:
            self.assertIn(row['source_id'],source_ids)
            self.assertEqual(row['analysis_basis'],'UNKNOWN')
            self.assertEqual(row['reuse_permission'],'UNKNOWN')

    def test_reported_totals_preserved_not_normalized(self):
        payload=json.loads((SEED.parent/'commercial-analysis-candidates.json').read_text(encoding='utf-8'))
        expected={'gs245-analysis-candidate':100.0,'opal-dbx2-analysis-candidate':99.45,'electromix-ta-analysis-candidate':124.0}
        for row in payload['records']:
            total=sum(row['oxides'].values())
            if row['loi_pct'] is not None:
                total+=row['loi_pct']
            self.assertAlmostEqual(total,expected[row['id']],places=8)
