"""Source transcription checks, not viscosity-model accuracy tests."""
import json
from pathlib import Path
import unittest

from pipelines.ingestion.viscosity_tables import cell, lines, parse_s3, parse_s4, EXPECTED_COUNTS

ROOT = Path(__file__).resolve().parents[1]


class ViscosityTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / "data/reference/conte-2018-viscosity-staging.json").read_text(encoding="utf-8"))

    def test_counts_and_unique_temperatures(self):
        rows = self.doc["viscosity_rows"]
        self.assertEqual(len(rows), 185)
        self.assertEqual(len({(r["sample_id"], r["temperature"]["value"]) for r in rows}), 185)
        for sample, count in EXPECTED_COUNTS.items():
            self.assertEqual(sum(r["sample_id"] == sample for r in rows), count)

    def test_visual_golden_rows_cover_every_sample(self):
        # Hand-read from rendered PDF pages 4-6, not computed by the extractor.
        cases = {("IGC", 1200): (4.34, 4.29, 3.53), ("MNV", 706): (10.71, 11.28, 8.63),
                 ("MDV", 955): (8.92, 9.11, 6.19), ("MST", 689): (11.60, 12.70, 10.70),
                 ("CI_OF", 780): (10.35, 9.80, 7.53), ("AMS-B1", 694): (11.18, 11.83, 9.21),
                 ("AMS-D1", 684): (11.29, 12.14, 9.46), ("G.2000", 737): (8.99, 9.45, 7.36),
                 ("Trachyte", 1258): (3.41, 3.49, 2.88), ("Phonolite", 1344): (2.86, 2.86, 2.32)}
        for key, expected in cases.items():
            row = next(r for r in self.doc["viscosity_rows"] if (r["sample_id"], r["temperature"]["value"]) == key)
            self.assertEqual(tuple(row["viscosity"][m]["value"] for m in ("experimental", "giordano", "fluegel")), expected)

    def test_split_label_and_page_continuation(self):
        phonolite = [r for r in self.doc["viscosity_rows"] if r["sample_id"] == "Phonolite"]
        self.assertEqual([r["temperature"]["value"] for r in phonolite[:6]], [616, 625, 638, 647, 659, 668])
        self.assertEqual([r["source_locator"]["physical_page"] for r in phonolite[:6]], [5, 5, 5, 5, 6, 6])

    def test_unsorted_source_order_preserved(self):
        mdv = [r["temperature"]["value"] for r in self.doc["viscosity_rows"] if r["sample_id"] == "MDV"]
        self.assertEqual(mdv[-2:], [818, 955])

    def test_s3_zero_is_not_missing(self):
        samples = {r["sample_id"]: r for r in self.doc["compositions"]}
        self.assertEqual(samples["MST"]["composition"]["P2O5"]["value"], 0)
        self.assertIsNone(samples["AMS-B1"]["composition"]["P2O5"]["value"])
        self.assertEqual(samples["AMS-B1"]["composition"]["P2O5"]["raw_text"], "—")
        self.assertEqual(samples["IGC"]["composition"]["FeO"]["value"], 3.4)
        self.assertNotIn("Fe2O3", samples["IGC"]["composition"])

    def test_no_invented_basis_or_normalization(self):
        for row in self.doc["compositions"]:
            self.assertIsNone(row["unit"])
            self.assertEqual(row["analysis_basis"], "UNKNOWN")
            self.assertFalse(row["normalization_applied"])
        self.assertNotEqual(self.doc["compositions"][0]["reported_numeric_sum"], 100)

    def test_epistemic_labels_and_units(self):
        for row in self.doc["viscosity_rows"]:
            self.assertEqual(row["temperature"]["unit"], "degC")
            for name, result in row["viscosity"].items():
                self.assertEqual(result["evidence_kind"], "OBSERVED" if name == "experimental" else "PREDICTED")
                self.assertEqual(result["qualifier"], "REPORTED")
                self.assertEqual(result["unit"], "log10(Pa.s)")
                self.assertIsNone(result["uncertainty"])
                self.assertEqual(len(result["bbox_pdf_points"]), 4)

    def test_no_engine_or_training_promotion(self):
        self.assertEqual(self.doc["status"], "RESEARCH_QUARANTINE")
        for key in ("core_engine_eligible", "training_enabled", "product_release_approved"):
            self.assertFalse(self.doc[key])
        self.assertFalse(self.doc["transcription"]["independent_second_reviewer"])

    def test_malformed_cell_rejected(self):
        for raw in ("NaN", "Infinity", "1,2", "-1", "unknown", ""):
            with self.assertRaisesRegex(ValueError, "INVALID_CELL"):
                cell({"text": raw})

    def test_changed_layout_rejected(self):
        class EmptyPage:
            def extract_words(self):
                return []
        with self.assertRaisesRegex(ValueError, "S3_SAMPLES_CHANGED"):
            parse_s3(EmptyPage())
        with self.assertRaisesRegex(ValueError, "S4_ROW_COUNTS_CHANGED"):
            parse_s4([EmptyPage()] * 6)

    def test_coordinate_line_grouping(self):
        words = [{"text": "B", "top": 10.1, "x0": 20},
                 {"text": "C", "top": 25, "x0": 10}, {"text": "A", "top": 10, "x0": 10}]
        self.assertEqual([[w["text"] for w in r] for r in lines(words)], [["A", "B"], ["C"]])


if __name__ == "__main__":
    unittest.main()
