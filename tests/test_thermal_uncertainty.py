from dataclasses import replace
import random
import unittest

from research.thermal.core import Curve, Scenario, ModelInputError
from research.thermal.uncertainty import propagate


class UncertaintyTests(unittest.TestCase):
    def setUp(self):
        g = Curve("g", "synthetic:test", "SYNTHETIC", ((0, 8e-6), (600, 8e-6)))
        b = replace(g, material_id="b", points=((0, 6e-6), (600, 6e-6)))
        self.scenario = Scenario(g, b, 520, 20, 100)
        self.options = dict(glaze_half_width_per_k=.5e-6, body_half_width_per_k=.5e-6,
                            samples=2000, seed=20260922)

    def run_model(self, **options):
        return propagate(self.scenario, **(self.options | options))

    def test_replay_and_global_rng_unchanged(self):
        before = random.getstate()
        self.assertEqual(self.run_model(), self.run_model())
        self.assertEqual(before, random.getstate())

    def test_analytical_moments_and_support(self):
        r = self.run_model(samples=20000)
        self.assertAlmostEqual(r["analytical_check"]["mean"], -.001)
        variance = 500**2 * (2 * (.5e-6)**2) / 3
        self.assertAlmostEqual(r["analytical_check"]["variance"], variance, places=16)
        self.assertLess(abs(r["mean"] + .001), 5 * (variance / 20000)**.5)
        self.assertLess(abs(r["sample_standard_deviation"]**2 / variance - 1), .04)
        self.assertAlmostEqual(r["support_bounds"]["min"], -.0015)
        self.assertAlmostEqual(r["support_bounds"]["max"], -.0005)
        self.assertTrue(r["support_bounds"]["min"] <= r["percentiles"]["p2_5"] <=
                        r["percentiles"]["p50"] <= r["percentiles"]["p97_5"] <= r["support_bounds"]["max"])

    def test_zero_width(self):
        r = self.run_model(glaze_half_width_per_k=0, body_half_width_per_k=0)
        self.assertEqual(r["sample_standard_deviation"], 0)
        self.assertEqual(r["percentiles"]["p2_5"], r["percentiles"]["p97_5"])

    def test_no_failure_probability(self):
        r = self.run_model()
        self.assertIsNone(r["fracture_probability"]["value"])
        self.assertEqual(r["fracture_probability"]["status"], "UNAVAILABLE")
        self.assertIn("SYNTHETIC", r["qualifiers"])

    def test_bad_parameters(self):
        for name, values in {"samples": [True, 99, 100001, 100.5],
                             "seed": [True, -1, 2**32, "1"],
                             "glaze_half_width_per_k": [-1, True, float("nan"), float("inf")]}.items():
            for value in values:
                with self.subTest(name=name, value=value), self.assertRaises(ModelInputError):
                    self.run_model(**{name: value})

    def test_invalid_support_aborts(self):
        with self.assertRaisesRegex(ModelInputError, "SMALL_STRAIN"):
            self.run_model(glaze_half_width_per_k=.01)

    def test_measured_input_is_not_accepted_as_assumed_uncertainty(self):
        self.scenario = replace(self.scenario, glaze=replace(self.scenario.glaze, data_kind="MEASURED"))
        with self.assertRaisesRegex(ModelInputError, "SYNTHETIC_ONLY"):
            self.run_model()

    def test_input_hash_tracks_seed(self):
        self.assertNotEqual(self.run_model()["input_hash"], self.run_model(seed=1)["input_hash"])

    def test_zero_delta_t(self):
        self.scenario = replace(self.scenario, target_temperature_c=520)
        r = self.run_model()
        self.assertEqual(r["mean"], 0)
        self.assertEqual(r["sample_standard_deviation"], 0)
