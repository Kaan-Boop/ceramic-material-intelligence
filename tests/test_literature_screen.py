import unittest
from scripts.screen_literature import screen
from scripts.collect_literature import title_key


class LiteratureScreenTests(unittest.TestCase):
    def row(self, title, kind='journal-article', domain='DOMAIN_TERM_PRESENT'):
        return dict(title=title,publication_type=kind,title_screen=domain)

    def test_direct_and_adjacent_are_only_candidates(self):
        self.assertEqual(screen(self.row('Porcelain glaze viscosity')), 'DIRECT_TOPIC_CANDIDATE')
        self.assertEqual(screen(self.row('Silicate melt viscosity')), 'ADJACENT_MATERIALS_CANDIDATE')

    def test_secondary_and_offscope(self):
        for title in ['ChemInform Abstract: glaze chemistry', 'Dental ceramic implant', 'Erratum: glaze viscosity']:
            self.assertEqual(screen(self.row(title)), 'LIKELY_OFF_SCOPE_OR_SECONDARY_NOTICE')

    def test_nonresearch_and_unknown(self):
        self.assertEqual(screen(self.row('Glaze', 'peer-review')), 'OTHER_DOCUMENT_TYPE')
        self.assertEqual(screen(self.row('Unknown',domain='REVIEW_REQUIRED')), 'MANUAL_TITLE_REVIEW_REQUIRED')

    def test_title_normalization(self):
        self.assertEqual(title_key('Glaze: Viscosity'), title_key('GLAZE viscosity'))
