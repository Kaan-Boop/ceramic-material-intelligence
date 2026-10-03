import gzip
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from pipelines.ingestion.local_glazy import stage
from research.local_recipe_archive import get_staged_record

class StagingTests(unittest.TestCase):
    def test_missing_fields_errors_and_recipe_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive, out = Path(tmp)/'raw.gz', Path(tmp)/'out.sqlite'
            text = '''-
  ID: 1
  Type: Recipe
  Ingredients:
    - ID: 2
      Percentage: 0
    - ID: 999
-
  ID: 2
  Type: Recipe
  Percent Analysis:
    SiO2: 0
-
  ID: 3
  ID: 4
  Type: Material
'''
            with gzip.open(archive,'wt',encoding='utf-8') as f:
                f.write(text)
            r=stage(archive,out)
            self.assertEqual((r['accepted'],r['rejected']),(2,1))
            self.assertEqual(r['checks']['recipe_target_rows']['value'],1)
            self.assertEqual(r['checks']['unresolved_target_rows']['value'],1)
            self.assertFalse(get_staged_record(1,out)['engine_eligible'])
            self.assertNotIn('Percent Analysis',get_staged_record(1,out)['record'])
            self.assertIsNone(get_staged_record(100,out))
            with closing(sqlite3.connect(out)) as db:
                rows=[json.loads(row[0]) for row in db.execute('SELECT payload FROM records ORDER BY seq')]
                self.assertNotIn('Percent Analysis',rows[0])
                self.assertEqual(rows[1]['Percent Analysis']['SiO2'],0)
            with self.assertRaises(FileExistsError):
                stage(archive,out)
