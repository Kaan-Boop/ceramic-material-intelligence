"""Hand-calculated metrics, explicit alignment, provenance and falsification cases."""
from copy import deepcopy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from research.process.outcomes import OutcomeInputError
from research.thermal.kiln_1d import ThermalInputError, simulate
from research.thermal.validation import ThermalComparisonError, evaluate

FIXTURE = Path(__file__).resolve().parents[1] / "data/fixtures/kiln-thermal-comparison-synthetic.json"


class ThermalComparisonTests(unittest.TestCase):
    def setUp(self):
        self.request = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_independent_equilibrium_oracle(self):
        report = evaluate(self.request)
        metrics = report["comparison"]["metrics"]
        self.assertAlmostEqual(metrics["bias_C"], 0)
        self.assertAlmostEqual(metrics["mae_C"], 4/3)
        self.assertAlmostEqual(metrics["rmse_C"], math.sqrt(8/3))
        self.assertAlmostEqual(metrics["max_absolute_error_C"], 2)
        self.assertEqual([r["residual_c"] for r in report["pairs"]], [2, -2, 0])
        self.assertEqual(report["time_interpolated_count"], 1)
        self.assertEqual(report["time_exact_count"], 2)
        self.assertEqual(report["probe_depth_m"], .01)
        self.assertEqual(report["observed_real_specimen_count"], 0)
        self.assertEqual(report["acceptance_status"], "NOT_ASSESSED")
        self.assertIsNone(report["uncertainty"])

    def test_explicit_linear_alignment_uses_prediction_not_modified_observation(self):
        self.request["case"]["schedule"]["points"][-1].update(gas_c=300, wall_c=330)
        original = deepcopy(self.request)
        report = evaluate(self.request)
        thermal = simulate(self.request["case"])
        expected = (thermal["series"][0]["layer_midpoint_c"]["inert_substrate"] +
                    thermal["series"][1]["layer_midpoint_c"]["inert_substrate"])/2
        self.assertAlmostEqual(report["pairs"][1]["predicted_c"], expected)
        self.assertEqual(report["pairs"][1]["observed_c"], 22)
        self.assertEqual(report["pairs"][1]["alignment"], {"method": "LINEAR", "left_time_s": 0, "right_time_s": 30, "right_weight": .5})
        self.assertEqual(self.request, original)

    def test_exact_policy_accepts_only_existing_times(self):
        self.request["alignment"] = {"method": "EXACT"}
        with self.assertRaisesRegex(ThermalComparisonError, "EXACT_SAMPLE_TIME_REQUIRED"):
            evaluate(self.request)
        self.request["observation"]["record"]["samples"][1]["time_s"] = 30
        self.assertEqual(evaluate(self.request)["time_interpolated_count"], 0)

    def test_gap_limit_and_no_extrapolation(self):
        self.request["alignment"]["max_interval_s"] = 29
        with self.assertRaisesRegex(ThermalComparisonError, "INTERPOLATION_INTERVAL_TOO_LARGE"):
            evaluate(self.request)
        self.request["alignment"]["max_interval_s"] = 30
        self.request["observation"]["record"]["samples"][-1]["time_s"] = 61
        with self.assertRaisesRegex(ThermalComparisonError, "OBSERVATION_OUTSIDE_SIMULATION_TIME"):
            evaluate(self.request)

    def test_surface_probes_use_true_surface_not_cell_center(self):
        self.request["case"]["schedule"]["points"][-1].update(gas_c=300, wall_c=330)
        for kind, key, depth in [("LEFT_SURFACE", "left_surface_c", 0), ("RIGHT_SURFACE", "right_surface_c", .02)]:
            self.request["probe"] = self.request["observation"]["probe"] = {"kind": kind}
            result = evaluate(self.request)
            last = result["thermal_report"]["series"][-1]
            self.assertEqual(result["pairs"][-1]["predicted_c"], last[key])
            self.assertEqual(result["probe_depth_m"], depth)
            self.assertNotEqual(last[key], last["cell_temperature_c"][0])

    def test_midpoint_depth_respects_layer_offsets(self):
        coating = deepcopy(self.request["case"]["layers"][0])
        coating.update(layer_id="coating", thickness_m=.002)
        self.request["case"]["layers"].append(coating)
        self.request["probe"] = self.request["observation"]["probe"] = {"kind": "LAYER_MIDPOINT", "layer_id": "coating"}
        self.assertAlmostEqual(evaluate(self.request)["probe_depth_m"], .021)

    def test_probe_and_unknown_layer_rejected(self):
        self.request["observation"]["probe"] = {"kind": "LEFT_SURFACE"}
        with self.assertRaisesRegex(ThermalComparisonError, "SENSOR_PROBE_MISMATCH"):
            evaluate(self.request)
        for target in (self.request, self.request["observation"]):
            target["probe"] = {"kind": "LAYER_MIDPOINT", "layer_id": "missing"}
        with self.assertRaisesRegex(ThermalComparisonError, "UNKNOWN_PROBE_LAYER"):
            evaluate(self.request)

    def test_no_time_shift_or_context_reassignment(self):
        self.request["observation"]["time_origin_ref"] = "different-clock"
        with self.assertRaisesRegex(ThermalComparisonError, "TIME_ORIGIN_MISMATCH"):
            evaluate(self.request)
        self.request["observation"]["time_origin_ref"] = self.request["time_origin_ref"]
        for field in ("body_revision", "firing_run_id", "sensor_location", "specimen_id"):
            changed = deepcopy(self.request)
            changed["observation"]["record"]["context"][field] = "different"
            with self.subTest(field=field), self.assertRaisesRegex(ThermalComparisonError, "SYSTEM_OR_SENSOR_MISMATCH"):
                evaluate(changed)

    def test_synthetic_inputs_cannot_be_paired_with_real_measurement(self):
        self.request["observation"]["record"]["data_kind"] = "REAL"
        with self.assertRaisesRegex(ThermalComparisonError, "REAL_SYNTHETIC_MISMATCH"):
            evaluate(self.request)

    def test_real_declared_inputs_still_do_not_establish_validation(self):
        # This tests contract labels only. It does not introduce a real dataset.
        case = self.request["case"]
        for group in [*case["layers"], *case["boundary"].values(), case["schedule"]]:
            group.update(input_kind="REPORTED", source_ref="contract-test:declared-source-not-verified")
        self.request["observation"]["record"]["data_kind"] = "REAL"
        self.request["observation"]["dataset_role"] = "HELD_OUT"
        result = evaluate(self.request)
        self.assertEqual(result["observed_real_specimen_count"], 1)
        self.assertEqual(result["physical_validation"], "NOT_ESTABLISHED")
        self.assertEqual(result["acceptance_status"], "NOT_ASSESSED")
        self.assertEqual(result["qualifier"], "PAIRED_COMPARISON_NOT_VALIDATION_APPROVAL")
        self.assertIn("SENSOR_CALIBRATION_UNKNOWN", result["warnings"])

    def test_unknown_uncertainty_not_zero_or_model_confidence(self):
        result = evaluate(self.request)
        self.assertIn("SENSOR_UNCERTAINTY_UNKNOWN", result["warnings"])
        self.request["observation"]["sensor"].update(standard_uncertainty_c=.5, calibration_ref="fixture:certificate")
        result = evaluate(self.request)
        self.assertNotIn("SENSOR_UNCERTAINTY_UNKNOWN", result["warnings"])
        self.assertIsNone(result["uncertainty"])
        self.assertEqual(result["input_snapshot"]["observation"]["sensor"]["standard_uncertainty_c"], .5)

    def test_kiln_observation_and_bad_samples_fail_before_solver(self):
        cases = []
        invalid = deepcopy(self.request); invalid["observation"]["record"]["temperature_basis"] = "PROGRAMMED_KILN"; cases.append(invalid)
        invalid = deepcopy(self.request); invalid["observation"]["record"]["samples"][0]["temperature_c"] = float("nan"); cases.append(invalid)
        invalid = deepcopy(self.request); invalid["observation"]["record"]["samples"][1]["time_s"] = 0; cases.append(invalid)
        for invalid in cases:
            with patch("research.thermal.validation.simulate") as solver, self.assertRaises(OutcomeInputError):
                evaluate(invalid)
            solver.assert_not_called()

    def test_strict_schema_and_sensor_numeric_validation(self):
        for value in (-1, True, float("inf")):
            self.request["observation"]["sensor"]["standard_uncertainty_c"] = value
            with self.assertRaises(OutcomeInputError):
                evaluate(self.request)
        self.request["observation"]["sensor"]["standard_uncertainty_c"] = None
        for key, value in [("alignment", {"method": "AUTO"}), ("probe", {"kind": "GAS"}), ("schema_version", "unknown")]:
            invalid = deepcopy(self.request); invalid[key] = value
            with self.subTest(key=key), self.assertRaises(ThermalComparisonError):
                evaluate(invalid)
        invalid = deepcopy(self.request); invalid["predicted_samples"] = []
        with self.assertRaises(ThermalComparisonError):
            evaluate(invalid)

    def test_preserves_input_and_hash_binds_observation_and_solver(self):
        before = deepcopy(self.request)
        first = evaluate(self.request)
        self.assertEqual(first, evaluate(self.request))
        self.assertEqual(self.request, before)
        self.request["observation"]["record"]["samples"][0]["temperature_c"] += 1
        second = evaluate(self.request)
        self.assertNotEqual(first["input_hash"], second["input_hash"])
        self.assertEqual(first["thermal_report"]["input_hash"], second["thermal_report"]["input_hash"])
        self.assertEqual(first["input_snapshot"], before)

    def test_thermal_domain_failure_is_not_turned_into_comparison(self):
        self.request["case"]["layers"][0]["valid_temperature_c"] = [0, 10]
        with self.assertRaises(ThermalInputError):
            evaluate(self.request)


if __name__ == "__main__":
    unittest.main()
