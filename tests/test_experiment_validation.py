"""Observed/calculated comparison tests."""

import unittest

from research.process.experiment_validation import (
    ExperimentValidationError,
    compare_observed_outcomes,
)


CALCULATED = {
    "sections": {
        "gloss": {"status": "AVAILABLE", "values": {"mean_gu": 42.0}},
        "porosity": {"status": "UNAVAILABLE", "values": {}},
    }
}
CONTEXT = {
    "body_analysis_id": "body-v1",
    "glaze_revision_id": "glaze-v1",
    "firing_run_id": "kiln-run-1",
    "application_id": "dip-1",
}


class ExperimentValidationTests(unittest.TestCase):
    def test_compares_replicates_and_counts_independent_specimens(self):
        result = compare_observed_outcomes(
            CALCULATED,
            [
                {
                    "observable": "gloss_mean_gu",
                    "value": 50,
                    "unit": "GU",
                    "specimen_id": "tile-a",
                    "source_ref": "lab-book:1",
                    "method": "60 degree gloss meter",
                    "status": "MEASURED",
                },
                {
                    "observable": "gloss_mean_gu",
                    "value": 46,
                    "unit": "GU",
                    "specimen_id": "tile-b",
                    "source_ref": "lab-book:2",
                    "method": "60 degree gloss meter",
                    "status": "MEASURED",
                },
            ],
            experiment_id="exp-1",
            context=CONTEXT,
        )

        gloss = result["comparisons"]["gloss_mean_gu"]
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(gloss["status"], "AVAILABLE")
        self.assertEqual(gloss["observed"], 48.0)
        self.assertEqual(gloss["residual_observed_minus_calculated"], 6.0)
        self.assertEqual(gloss["independent_specimen_count"], 2)
        self.assertIn("water_absorption_mass_pct", result["unavailable_sections"])

    def test_reported_observation_is_not_promoted_to_measured(self):
        result = compare_observed_outcomes(
            CALCULATED,
            [{
                "observable": "gloss_mean_gu",
                "value": 50,
                "unit": "GU",
                "specimen_id": "tile-a",
                "source_ref": "notebook:1",
                "method": "visual estimate",
                "status": "REPORTED",
            }],
            experiment_id="exp-2",
            context=CONTEXT,
        )
        self.assertEqual(result["comparisons"]["gloss_mean_gu"]["observation_statuses"], ["REPORTED"])
        self.assertTrue(result["warnings"])

    def test_unknown_quantity_is_rejected(self):
        with self.assertRaises(ExperimentValidationError) as context:
            compare_observed_outcomes(
                CALCULATED,
                [{
                    "observable": "surface_color",
                    "value": 1,
                    "unit": "RGB",
                    "specimen_id": "tile-a",
                    "source_ref": "lab-book:1",
                    "method": "camera",
                    "status": "MEASURED",
                }],
                experiment_id="exp-3",
                context=CONTEXT,
            )
        self.assertEqual(str(context.exception), "UNSUPPORTED_OBSERVABLE")


if __name__ == "__main__":
    unittest.main()
