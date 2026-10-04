"""Contract tests for material-agnostic simulation scenarios."""
import unittest

from research.simulation.scenario import (
    FiringSchedule,
    FiringSegment,
    GeometrySpec,
    LayerSpec,
    MaterialRef,
    SimulationScenario,
    SimulationTarget,
)


def make_scenario(objective="fit-and-surface"):
    body = LayerSpec(
        layer_id="body",
        materials=(MaterialRef("analysis/porcelain-001", "BODY", amount_g=1000),),
    )
    engobe = LayerSpec(
        layer_id="engobe-a",
        materials=(MaterialRef("analysis/engobe-iron-001", "ENGOBE", amount_g=120),),
        application_method="DIP",
        coat_count=1,
        dry_thickness_um=180,
        drying_minutes=45,
    )
    glaze = LayerSpec(
        layer_id="glaze-a",
        materials=(
            MaterialRef("analysis/frit-001", "GLAZE", amount_g=80),
            MaterialRef("analysis/cobalt-oxide-001", "ADDITION", amount_g=2),
        ),
        application_method="SPRAY",
        coat_count=2,
        wet_thickness_um=420,
    )
    bisque = FiringSchedule(
        name="bisque-test",
        start_c=20,
        segments=(FiringSegment(600, 100), FiringSegment(1000, 150, 20)),
        atmosphere="OXIDATION",
    )
    final = FiringSchedule(
        name="high-fire-test",
        start_c=20,
        segments=(FiringSegment(1200, 120), FiringSegment(1250, 60, 15)),
        atmosphere="OXIDATION",
    )
    return SimulationScenario(
        scenario_id="scenario-porcelain-blue",
        body=body,
        layers=(engobe, glaze),
        bisque=bisque,
        final_firing=final,
        geometry=GeometrySpec("TILE", 8, length_mm=100, width_mm=100),
        target=SimulationTarget(
            objective=objective,
            requested_outputs=("melt_fraction", "fit_risk", "surface_state"),
            reference_temperature_c=1250,
        ),
        metadata={"purpose": "research-fixture", "evidence_kind": "CALCULATED"},
    )


class SimulationScenarioTests(unittest.TestCase):
    def test_supports_arbitrary_material_combinations_and_layers(self):
        scenario = make_scenario()
        self.assertEqual(scenario.body.materials[0].analysis_id, "analysis/porcelain-001")
        self.assertEqual([layer.layer_id for layer in scenario.layers], ["engobe-a", "glaze-a"])
        self.assertEqual(scenario.layers[1].materials[1].role, "ADDITION")
        self.assertEqual(scenario.snapshot()["target"]["objective"], "fit-and-surface")

    def test_hash_is_stable_for_same_snapshot(self):
        self.assertEqual(make_scenario().input_hash(), make_scenario().input_hash())

    def test_target_change_changes_hash(self):
        self.assertNotEqual(make_scenario().input_hash(), make_scenario("colour-range").input_hash())

    def test_duplicate_layer_ids_are_rejected(self):
        duplicate = LayerSpec("glaze-a", (MaterialRef("analysis/other", "OVERGLAZE"),))
        with self.assertRaises(ValueError):
            SimulationScenario(
                scenario_id="duplicate",
                body=make_scenario().body,
                layers=(duplicate, make_scenario().layers[1]),
                bisque=None,
                final_firing=make_scenario().final_firing,
                geometry=make_scenario().geometry,
                target=make_scenario().target,
            )

    def test_body_must_be_separate_and_named_body(self):
        with self.assertRaises(ValueError):
            SimulationScenario(
                scenario_id="wrong-body",
                body=LayerSpec("porcelain", (MaterialRef("analysis/body", "BODY"),)),
                layers=(),
                bisque=None,
                final_firing=make_scenario().final_firing,
                geometry=make_scenario().geometry,
                target=make_scenario().target,
            )

    def test_invalid_application_and_measurement_values_are_rejected(self):
        with self.assertRaises(ValueError):
            MaterialRef("analysis/x", "GLAZE", amount_g=0)
        with self.assertRaises(ValueError):
            MaterialRef("analysis/x", "NOT_A_ROLE")
        with self.assertRaises(ValueError):
            LayerSpec("glaze", (MaterialRef("analysis/x", "GLAZE"),), dry_thickness_um=-1)
        with self.assertRaises(ValueError):
            LayerSpec("glaze", (MaterialRef("analysis/x", "GLAZE"),), application_method="NOT_A_METHOD")
        with self.assertRaises(ValueError):
            FiringSegment(2000, 100)
        with self.assertRaises(ValueError):
            FiringSegment(float("nan"), 100)
        with self.assertRaises(ValueError):
            GeometrySpec("TILE", 0)


if __name__ == "__main__":
    unittest.main()
