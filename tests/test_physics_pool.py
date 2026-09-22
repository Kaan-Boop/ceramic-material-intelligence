import unittest
from pipelines.ingestion.physics_pool import paper_metadata, table_extract


class PhysicsPoolTests(unittest.TestCase):
    def article(self, license_url='https://creativecommons.org/licenses/by/4.0/'):
        return f'''<article><front><article-meta><article-id pub-id-type="doi">10.example/test</article-id>
        <title-group><article-title>Synthetic test</article-title></title-group>
        <contrib-group><contrib contrib-type="author"><name><given-names>A</given-names><surname>B</surname></name></contrib></contrib-group>
        <permissions><license>{license_url}</license></permissions></article-meta></front>
        <body><table-wrap id="t1"><label>Table 1</label><caption><p>Not numeric validation</p></caption>
        <table><tr><td>UNKNOWN</td></tr></table></table-wrap></body></article>'''.encode()

    def test_license_and_author(self):
        root, meta = paper_metadata(self.article())
        self.assertEqual(meta['source_author'], 'A B')
        self.assertEqual(meta['source_license'], 'CC-BY-4.0')
        tables = table_extract(root)
        self.assertEqual(len(tables), 1)
        self.assertIn('UNKNOWN', tables[0]['xml'])

    def test_noncommercial_and_unknown_are_not_admitted(self):
        for license_url in ('https://creativecommons.org/licenses/by-nc/4.0/', 'unknown'):
            with self.assertRaisesRegex(ValueError, 'LICENSE'):
                paper_metadata(self.article(license_url))

    def test_missing_doi(self):
        raw = self.article().replace(b'<article-id pub-id-type="doi">10.example/test</article-id>', b'')
        with self.assertRaisesRegex(ValueError, 'DOI'):
            paper_metadata(raw)
