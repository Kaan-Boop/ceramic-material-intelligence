from copy import deepcopy
import json
import unittest
from research.commercial_catalogue import SEED, build
from research.process.reported_properties import DATA, validate_bundle, compare_reported_windows, report


class ReportedPropertiesTests(unittest.TestCase):
    def setUp(self):
        self.bundle=json.loads(DATA.read_text(encoding='utf-8'))
        self.catalogue=build(json.loads(SEED.read_text(encoding='utf-8')))
        self.products={r['id']:r for r in self.bundle['products']}

    def test_foreign_keys(self):
        self.assertTrue(validate_bundle(self.bundle,self.catalogue))

    def test_orphan_rejected(self):
        self.bundle['products'][0]['catalogue_key']='missing'
        with self.assertRaises(ValueError): validate_bundle(self.bundle,self.catalogue)

    def test_duplicate_rejected(self):
        self.bundle['products'].append(deepcopy(self.bundle['products'][0]))
        with self.assertRaises(ValueError): validate_bundle(self.bundle,self.catalogue)

    def test_conflict_even_when_peak_inside_both(self):
        for key in ('tr-refsan-159','tr-refsan-259'):
            for peak in (1190,1210):
                result=compare_reported_windows(self.products[key],'GLAZE',peak)
                self.assertEqual(result['code'],'CONFLICTING_SOURCE_WINDOWS')
                self.assertIsNone(result['probability'])

    def test_bisque_not_affected_by_glaze_conflict(self):
        self.assertEqual(compare_reported_windows(self.products['tr-refsan-159'],'BISQUE',950)['code'],'WITHIN_REPORTED_WINDOW')

    def test_no_single_point_as_range(self):
        self.assertEqual(compare_reported_windows(self.products['tr-crafist-akcini'],'GLAZE',1040)['code'],'SINGLE_TARGET_NO_OPERATING_RANGE')

    def test_normal_window_and_no_mutation(self):
        row=self.products['tr-akasya-stoneware']
        before=deepcopy(row)
        self.assertEqual(compare_reported_windows(row,'GLAZE',1210)['code'],'WITHIN_REPORTED_WINDOW')
        self.assertEqual(row,before)

    def test_chemistry_unmodified(self):
        result=report(self.bundle,self.catalogue)
        self.assertEqual(result['reported_candidate_totals']['tr-refsan-656'],99.8)
        self.assertEqual(result['new_accepted_analyses'],0)

    def test_bad_unit(self):
        self.bundle['products'][0]['properties'][0]['unit']='mm'
        with self.assertRaises(ValueError): validate_bundle(self.bundle,self.catalogue)

    def test_dates_not_refreshed_for_old_identity(self):
        rows={r['product_code']:r for r in self.catalogue if r['brand']=='Refsan'}
        self.assertEqual(rows['R24174']['retrieval_date'],'2026-09-22')
        self.assertEqual(rows['R24003']['retrieval_date'],'2026-09-23')

    def test_nonfinite_and_bool_peak_rejected(self):
        for value in (True,float('nan'),float('inf'),-1):
            with self.assertRaises(ValueError): compare_reported_windows(self.products['tr-refsan-159'],'GLAZE',value)

    def test_replay_and_change_hash(self):
        row=self.products['tr-akasya-stoneware']
        a=compare_reported_windows(row,'GLAZE',1210)
        self.assertEqual(a,compare_reported_windows(row,'GLAZE',1210))
        self.assertNotEqual(a['input_hash'],compare_reported_windows(row,'GLAZE',1200)['input_hash'])
