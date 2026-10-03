import unittest
from apps.api.app.main import library, material_list

class LibraryTests(unittest.TestCase):
    def test_counts_and_identity(self):
        rows=library()['records']
        self.assertEqual(len(rows),185)
        self.assertEqual(len({r['id'] for r in rows}),len(rows))
        self.assertEqual(sum(r['engine_eligible'] for r in rows),4)
        self.assertEqual(len(material_list()),4)

    def test_research_never_promoted(self):
        for r in library()['records']:
            if r['kind']!='IDEAL_MATERIAL':
                self.assertFalse(r['engine_eligible'])
                self.assertEqual(r['basis'],'UNKNOWN')
            self.assertTrue(r['source_url'].startswith('https://'))

    def test_body_windows_and_missing_chemistry(self):
        rows=library()['records']
        body=next(r for r in rows if r['brand']=='Akasya' and r['name']=='Stoneware Vakum Çamuru')
        self.assertEqual(body['windows'][0]['min_c'],1190)
        self.assertEqual(body['oxides'],{})
        conflict=next(r for r in rows if r['name']=='159 Stoneware Çamuru Vakumlu')
        self.assertEqual(len([w for w in conflict['windows'] if w['stage']=='GLAZE']),2)

if __name__=='__main__':unittest.main()
