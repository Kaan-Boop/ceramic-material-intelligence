import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from research.local_recipe_archive import search_recipes

class ArchiveTests(unittest.TestCase):
    def test_search_is_paginated_literal_and_not_engine_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fixture.sqlite'
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE recipes(id INTEGER PRIMARY KEY,name TEXT,subtype TEXT,cone TEXT,surface TEXT,ingredients_count INTEGER)')
                db.executemany('INSERT INTO recipes VALUES (?,?,NULL,NULL,NULL,0)', [(1,'A'),(2,'B'),(3,'100%')])
                db.commit()
            self.assertEqual(search_recipes(page_size=1, database=path)['total'], 3)
            self.assertEqual(len(search_recipes(page_size=1, database=path)['items']), 1)
            self.assertEqual(search_recipes('%', database=path)['total'], 1)
            self.assertEqual(search_recipes("' OR 1=1 --", database=path)['total'], 0)
            self.assertFalse(search_recipes(database=path)['engine_eligible'])
            self.assertEqual(search_recipes(category='ANALYSIS', database=path)['total'], 0)
            with self.assertRaises(ValueError):
                search_recipes(page=0, database=path)
