import copy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research.thermal.core import Curve, Scenario, ModelInputError, calculate, free_strain, sensitivity
from research.thermal.__main__ import run, unique_object

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/fixtures/thermal-synthetic.json"


class ThermalTests(unittest.TestCase):
    def setUp(self):
        self.g = Curve("test-glaze", "project:synthetic-test", "SYNTHETIC", ((0, 8e-6), (600, 8e-6)))
        self.b = replace(self.g, material_id="test-body", points=((0, 6e-6), (600, 6e-6)))
        self.s = Scenario(self.g, self.b, 520, 20, 100)
        self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_hand_calculation(self):
        result = calculate(self.s)
        self.assertAlmostEqual(result["glaze_free_strain"], -0.004, places=14)
        self.assertAlmostEqual(result["body_free_strain"], -0.003, places=14)
        self.assertAlmostEqual(result["mismatch_strain_glaze_minus_body"], -0.001, places=14)
        self.assertAlmostEqual(result["free_length_difference_mm"], -0.1, places=12)

    def test_identical_materials(self):
        self.assertEqual(calculate(replace(self.s, body=self.g))["mismatch_strain_glaze_minus_body"], 0)

    def test_reverse_path(self):
        self.assertEqual(free_strain(self.g, 520, 20), -free_strain(self.g, 20, 520))

    def test_zero_temperature_change(self):
        self.assertEqual(free_strain(self.g, 20, 20), 0)

    def test_piecewise_linear_exact_integral(self):
        curve = replace(self.g, points=((0, 2e-6), (100, 4e-6), (300, 8e-6)))
        self.assertAlmostEqual(free_strain(curve, 0, 300), 0.0015, places=14)
        self.assertAlmostEqual(free_strain(curve, 50, 200), 0.000675, places=14)

    def test_partition_invariance(self):
        self.assertAlmostEqual(free_strain(self.g, 520, 20),
                               free_strain(self.g, 520, 170) + free_strain(self.g, 170, 20))

    def test_length_scaling_not_strain_scaling(self):
        a, b = calculate(self.s), calculate(replace(self.s, reference_length_mm=200))
        self.assertEqual(a["mismatch_strain_glaze_minus_body"], b["mismatch_strain_glaze_minus_body"])
        self.assertEqual(2 * a["free_length_difference_mm"], b["free_length_difference_mm"])

    def test_negative_cte_is_not_silently_rejected(self):
        curve = replace(self.g, points=((0, -1e-6), (600, -1e-6)))
        self.assertAlmostEqual(free_strain(curve, 520, 20), 0.0005)

    def test_no_extrapolation_even_zero_interval(self):
        for a, b in ((610, 20), (520, -1), (610, 610)):
            with self.subTest(a=a, b=b), self.assertRaisesRegex(ModelInputError, "OUTSIDE"):
                free_strain(self.g, a, b)

    def test_invalid_numbers(self):
        for value in (True, False, "20", None, float("nan"), float("inf"), 10**400):
            with self.subTest(value=str(value)[:20]), self.assertRaises(ModelInputError):
                replace(self.s, target_temperature_c=value)
            with self.assertRaises(ModelInputError):
                replace(self.g, points=((0, value), (600, 1e-6)))

    def test_invalid_length_and_absolute_zero(self):
        for length in (0, -1):
            with self.assertRaises(ModelInputError):
                replace(self.s, reference_length_mm=length)
        with self.assertRaisesRegex(ModelInputError, "ABSOLUTE_ZERO"):
            replace(self.s, target_temperature_c=-274)

    def test_invalid_curve_order_shape_and_provenance(self):
        for points in ((), ((0, 1e-6),), ((0, 1e-6), (0, 2e-6)), ((600, 1e-6), (0, 1e-6))):
            with self.subTest(points=points), self.assertRaises(ModelInputError):
                replace(self.g, points=points)
        with self.assertRaisesRegex(ModelInputError, "PROVENANCE"):
            replace(self.g, source_ref=" ")

    def test_mean_coefficient_and_unknown_units_rejected(self):
        for changes in ({"coefficient_kind": "MEAN"}, {"unit": "microstrain/K"}, {"data_kind": "UNKNOWN"}):
            with self.subTest(changes=changes), self.assertRaises(ModelInputError):
                replace(self.g, **changes)

    def test_scope_limit_not_failure_threshold(self):
        with self.assertRaisesRegex(ModelInputError, "SCOPE_EXCEEDED"):
            free_strain(replace(self.g, points=((0, 0.01), (600, 0.01))), 520, 20)

    def test_analytic_uniform_alpha_sensitivity(self):
        rows = sensitivity(self.s, {"glaze_alpha_offset_per_k": 0.5e-6})
        self.assertAlmostEqual(rows[0]["change_from_baseline_strain"], 0.00025)
        self.assertAlmostEqual(rows[1]["change_from_baseline_strain"], -0.00025)

    def test_temperature_sensitivity(self):
        row = sensitivity(self.s, {"target_temperature_c": 10})[1]
        self.assertAlmostEqual(row["change_from_baseline_strain"], 0.00002)

    def test_sensitivity_validation(self):
        for steps in ({"cooling_rate": 1}, {"target_temperature_c": 0}, {"target_temperature_c": 30}, []):
            with self.subTest(steps=steps), self.assertRaises(ModelInputError):
                sensitivity(self.s, steps)

    def test_reproducibility_and_no_input_mutation(self):
        original = copy.deepcopy(self.data)
        report = run(self.data)
        self.assertEqual(report, run(self.data))
        self.assertEqual(self.data, original)
        self.assertEqual(len(report["input_hash"]), 64)
        self.assertEqual(len(report["sensitivity_oat"]), 10)
        self.data["reference_length_mm"] = 110
        self.assertNotEqual(report["input_hash"], run(self.data)["input_hash"])
        self.data["sensitivity_steps"]["reference_length_mm"] = 20
        self.assertEqual(report["sensitivity_steps"]["reference_length_mm"], 10)

    def test_honest_result_labels(self):
        report = run(self.data)
        self.assertTrue(report["contains_synthetic_inputs"])
        self.assertEqual(report["evidence_kind"], "PREDICTED")
        self.assertIsNone(report["uncertainty"])
        self.assertIn("failure_probability", report["unavailable_sections"])
        self.assertIn("chemical_reactions", report["unavailable_sections"])

    def test_strict_json_schema_and_duplicates(self):
        for mutation in ({"firing_rate": 100}, {"schema_version": "other"}, {"glaze": {}}):
            with self.subTest(mutation=mutation), self.assertRaises(ModelInputError):
                run({**self.data, **mutation})
        with self.assertRaisesRegex(ModelInputError, "DUPLICATE"):
            json.loads('{"a": 1, "a": 2}', object_pairs_hook=unique_object)

    def test_cli_export_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "report.json"
            cmd = [sys.executable, "-X", "utf8", "-m", "research.thermal", str(FIXTURE), "--output", str(output)]
            first = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = output.read_bytes()
            self.assertEqual(json.loads(original)["values"], run(self.data)["values"])
            second = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(original, output.read_bytes())


if __name__ == "__main__":
    unittest.main()
