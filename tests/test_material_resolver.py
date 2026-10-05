"""Exact analysis resolution never falls back to fuzzy material names."""
import unittest

from research.material_resolver import MaterialResolutionError, library_snapshot, resolve_engine_analysis, resolve_materials, resolve_material


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

    def test_engine_adapter_returns_complete_snapshot_only_for_eligible_record(self):
        analysis = resolve_engine_analysis("pure_silica")
        self.assertTrue(analysis["complete"])
        self.assertEqual(analysis["analysis_id"], "pure_silica")
        research_only = next(record for record in library_snapshot() if record["kind"] == "CLAY_BODY")
        with self.assertRaises(MaterialResolutionError):
            resolve_engine_analysis(research_only["id"])


if __name__ == "__main__":
    unittest.main()
