"""Exact analysis resolution never falls back to fuzzy material names."""
import unittest

from research.material_resolver import MaterialResolutionError, resolve_materials, resolve_material


class MaterialResolverTests(unittest.TestCase):
    def test_theoretical_analysis_is_resolved_with_engine_property(self):
        record = resolve_material("pure_silica")
        self.assertEqual(record["status"], "THEORETICAL")
        records, inventory = resolve_materials(["pure_silica", "pure_silica"])
        self.assertEqual(len(records), 1)
        self.assertEqual(inventory["pure_silica"], {"oxide_analysis"})

    def test_unknown_or_display_name_does_not_resolve(self):
        for value in ("Saf silika", "generic-feldspar", ""):
            with self.assertRaises(MaterialResolutionError):
                resolve_material(value)


if __name__ == "__main__":
    unittest.main()
