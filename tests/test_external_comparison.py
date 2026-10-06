"""Comparison reports preserve uncertainty and do not invent missing values."""
import unittest

from research.external.comparison import (
    compare_calculated_reports,
    replay_comparison_snapshot,
    value_delta,
)


class ExternalComparisonTests(unittest.TestCase):
    def test_delta_and_percentage_are_directional(self):
        result = value_delta(2.0, 2.5)
        self.assertEqual(result["status"], "AVAILABLE")
        self.assertEqual(result["delta"], 0.5)
        self.assertEqual(result["delta_pct"], 25.0)

    def test_missing_values_stay_unavailable(self):
        result = value_delta(None, 2.5)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertIsNone(result["delta"])

    def test_comparison_is_partial_when_external_material_is_missing(self):
        internal = {
            "input_hash": "internal-hash",
            "engine_version": "engine/1",
            "umf_convention": "standard-flux-v1",
            "umf": {"values": {"SiO2": 3.0, "CaO": 0.5}},
            "ratios": {"SiO2_to_Al2O3_molar": {"value": 6.0}},
        }
        external = {
            "source": "OpenGlaze",
            "report": {
                "success": False,
                "missing_materials": ["Unknown clay"],
                "umf_formula": {"SiO2": 3.2},
                "ratios": {"sio2_al2o3": 6.4},
            },
        }
        result = compare_calculated_reports(
            internal,
            external,
            external_ingredients=[{"name": "Unknown clay", "amount": 10}],
            cone=6,
        )
        self.assertEqual(result["status"], "PARTIAL")
        self.assertIsNone(result["differences"]["umf"]["CaO"]["external"])
        self.assertTrue(any("tanımadı" in warning for warning in result["warnings"]))

    def test_replay_snapshot_passes_without_rerunning_external_engine(self):
        internal = {
            "input_hash": "internal-hash",
            "engine_version": "engine/1",
            "input_snapshot": {"ingredients": [{"analysis_id": "a", "amount": 100}]},
            "umf_convention": "standard-flux-v1",
            "umf": {"values": {"SiO2": 3.0, "CaO": 0.5}},
            "ratios": {"SiO2_to_Al2O3_molar": {"value": 6.0}},
        }
        external = {
            "source": "OpenGlaze",
            "report": {
                "success": True,
                "missing_materials": [],
                "umf_formula": {"SiO2": 3.2, "CaO": 0.4},
                "ratios": {"sio2_al2o3": 6.4},
            },
        }
        snapshot = compare_calculated_reports(
            internal,
            external,
            external_ingredients=[{"name": "Silica", "amount": 100}],
            cone=6,
        )

        replay = replay_comparison_snapshot(snapshot)

        self.assertEqual(replay["status"], "PASS")
        self.assertTrue(replay["input_hash_matches"])
        self.assertTrue(replay["differences_match"])

        snapshot["differences"]["umf"]["CaO"]["delta"] = 999
        tampered = replay_comparison_snapshot(snapshot)
        self.assertEqual(tampered["status"], "FAIL")
        self.assertTrue(tampered["input_hash_matches"])
        self.assertFalse(tampered["differences_match"])

    def test_replay_snapshot_requires_input_envelope(self):
        replay = replay_comparison_snapshot({
            "schema_version": "comparison-run-v1",
            "internal": {},
            "external": {},
        })
        self.assertEqual(replay["status"], "UNAVAILABLE")
        self.assertEqual(replay["reason"], "MISSING_INPUT_SNAPSHOT")


if __name__ == "__main__":
    unittest.main()
