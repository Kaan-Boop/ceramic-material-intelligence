"""Capability gates prevent unsupported simulation outputs from looking real."""
import unittest

from research.simulation.capabilities import assess_capabilities
from research.simulation.scenario import (
    FiringSchedule,
    FiringSegment,
    GeometrySpec,
    LayerSpec,
    MaterialRef,
    SimulationScenario,
    SimulationTarget,
)


def scenario(outputs=("oxide_composition", "firing_timeline", "melt_fraction", "fit_risk")):
    return SimulationScenario(
        scenario_id="generic-capability-fixture",
        body=LayerSpec("body", (MaterialRef("body-analysis", "BODY"),)),
        layers=(LayerSpec("glaze", (MaterialRef("glaze-analysis", "GLAZE"),), coat_count=2),),
        bisque=None,
        final_firing=FiringSchedule("test", 20, (FiringSegment(1220, 100, 10),), "OXIDATION"),
        geometry=GeometrySpec("TILE", 10, length_mm=100, width_mm=100),
        target=SimulationTarget("user-selected-target", outputs),
    )


class SimulationCapabilityTests(unittest.TestCase):
    def test_missing_inputs_do_not_become_fake_predictions(self):
        report = assess_capabilities(scenario())
        self.assertEqual(report["outputs"]["oxide_composition"]["status"], "UNAVAILABLE")
        self.assertEqual(report["outputs"]["melt_fraction"]["status"], "UNAVAILABLE")
        self.assertEqual(report["outputs"]["firing_timeline"]["status"], "AVAILABLE")

    def test_resolved_chemistry_and_cte_are_distinguished(self):
        inventory = {
            "body-analysis": {"oxide_analysis", "density", "cte"},
            "glaze-analysis": {"oxide_analysis", "cte"},
        }
        report = assess_capabilities(scenario(), inventory)
        self.assertEqual(report["outputs"]["oxide_composition"]["status"], "AVAILABLE")
        self.assertEqual(report["outputs"]["fit_risk"]["status"], "PARTIAL")
        self.assertEqual(report["outputs"]["fit_risk"]["evidence_kind"], "PREDICTED")

    def test_unknown_target_is_explicitly_unavailable(self):
        report = assess_capabilities(scenario(("my_future_model",)))
        self.assertEqual(report["outputs"]["my_future_model"]["status"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
