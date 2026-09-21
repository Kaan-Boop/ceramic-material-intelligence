import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipelines.ingestion.study_materials import candidate, cell, extract, xml_rows, build, thermal_reference
from pipelines.ingestion.acquire import article_authors
import xml.etree.ElementTree as ET


class StudyMaterialTests(unittest.TestCase):
    def test_jats_group_author_metadata(self):
        raw = '<article-meta><contrib-group content-type="author"><contrib><name><surname>Example</surname><given-names>A</given-names></name></contrib></contrib-group></article-meta>'
        self.assertEqual(article_authors(ET.fromstring(raw)), "A Example")
        with self.assertRaisesRegex(ValueError, "AUTHOR_METADATA_REVIEW_REQUIRED"):
            article_authors(ET.fromstring('<article-meta/>'))

    def test_dash_not_zero(self):
        self.assertIsNone(cell("Na2O", "–")["value"])
        self.assertEqual(cell("Na2O", "0")["value"], "0")

    def test_invalid_numbers(self):
        for value in ("NaN", "Infinity", "-1", "101"):
            with self.assertRaises(ValueError):
                cell("SiO2", value)

    def test_others_not_loi(self):
        r = candidate("s", "m", ["SiO2", "Others"], ["80", "20"])
        self.assertIn("LOI_WT_PCT_UNAVAILABLE", r["quality_flags"])
        self.assertFalse(r["core_engine_eligible"])

    def test_total_not_repaired(self):
        r = extract("sanitary-body-2022", b"")[0]
        self.assertEqual(r["reported_numeric_column_sum"], "101.9")
        self.assertIn("REPORTED_COLUMN_SUM_OUTSIDE_100_PLUS_MINUS_0_5", r["quality_flags"])
        self.assertEqual(r["measurements"][0]["value"], "52")

    def test_names_and_unknown_basis_preserved(self):
        records = extract("anorthite-2018", b"")
        self.assertIn("Cibelco", records[1]["manufacturer_as_reported"])
        self.assertEqual(records[0]["analysis_basis"], "UNKNOWN")
        self.assertIsNone(records[0]["analysis_date"])

    def test_no_duplicate_or_ragged_columns(self):
        for labels, values in ((["SiO2", "SiO2"], ["20", "20"]), (["SiO2"], [])):
            with self.assertRaises(ValueError):
                candidate("s", "m", labels, values)

    def test_xml_schema_changes_stop(self):
        raw = b'<article><table-wrap id="t"><table><thead><tr><th>A</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table></table-wrap></article>'
        self.assertEqual(xml_rows(raw, "t", ["A"]), [["1"]])
        for table_id, header in (("missing", ["A"]), ("t", ["B"])):
            with self.assertRaises(ValueError):
                xml_rows(raw, table_id, header)
        with self.assertRaisesRegex(ValueError, "TABLE_SPAN_CHANGED"):
            xml_rows(raw.replace(b'<td>', b'<td colspan="2">'), "t", ["A"])

    def test_builder_replay_and_archive_guards(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "receipts").mkdir()
            (root / "raw").mkdir()
            raw = b"synthetic archive integrity fixture, not real material data"
            digest = hashlib.sha256(raw).hexdigest()
            (root / "raw/doc").write_bytes(raw)
            receipt = {"created_at": "2026-09-21", "sources": {"test": {"source_license": "CC-BY-4.0", "rights_partition": "CC_BY_REFERENCE"}},
                       "failures": {}, "files": [{"source_id": "test", "filename": "article.pdf", "raw_path": "raw/doc", "sha256": digest, "source_url": "https://example.org/test"}]}
            path = root / "receipts/r.json"
            def save(doc):
                path.write_text(json.dumps(doc), encoding="utf-8")
            save(receipt)
            sample = candidate("test", "synthetic", ["SiO2"], ["100"])
            with patch("pipelines.ingestion.study_materials.REVIEWED", {"test": digest}), patch("pipelines.ingestion.study_materials.extract", return_value=[sample]):
                first = build(root)
                self.assertEqual(first, build(root))
                self.assertEqual(first["report"]["accepted_for_core"], 0)
                bad = copy.deepcopy(receipt)
                bad["sources"]["test"]["source_license"] = "UNKNOWN"
                save(bad)
                with self.assertRaisesRegex(ValueError, "SOURCE_RIGHTS_CHANGED"):
                    build(root)
                save(receipt)
                (root / "raw/doc").write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "SOURCE_REVIEW_REQUIRED"):
                    build(root)

    def test_missing_sources_not_accepted(self):
        with tempfile.TemporaryDirectory() as root:
            result = build(root)
            self.assertEqual(result["report"]["candidate_count"], 0)
            self.assertTrue(result["report"]["missing_reviewed_sources"])

    def test_thermal_means_not_instantaneous_curves(self):
        records = thermal_reference({"sha256": "synthetic", "source_url": "https://example.org/fixture"})
        self.assertEqual(len(records), 2)
        self.assertEqual(sum(len(r["intervals"]) for r in records), 12)
        for r in records:
            self.assertFalse(r["model_input_eligible"])
            self.assertEqual(r["quantity_kind"], "REPORTED_INTERVAL_MEAN_LINEAR_TEC")
            self.assertEqual(r["measurement_branch"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
