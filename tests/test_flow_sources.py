import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipelines.ingestion.flow_sources import (
    ARTICLES, immutable_write, parse_article, run, table_index, verify_receipt,
)


def article(license_path="by/4.0", doi="10.3390/ma11122475"):
    return f'''<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta>
    <article-id pub-id-type="doi">{doi}</article-id><title-group><article-title>Test</article-title></title-group>
    <contrib-group><contrib contrib-type="author"><name><surname>Researcher</surname><given-names>A</given-names></name></contrib></contrib-group>
    <permissions><license><license-p><ext-link xlink:href="https://creativecommons.org/licenses/{license_path}/">license</ext-link></license-p></license></permissions>
    </article-meta></front><body><table-wrap id="T1"><label>Table 1</label><caption>Test table</caption>
    <table><tbody><tr><th colspan="2">Unit</th></tr><tr><td rowspan="2">log<sub>10</sub></td><td/></tr></tbody></table>
    <table-wrap-foot>Estimated, not measured</table-wrap-foot></table-wrap></body></article>'''.encode()


class FlowSourceTests(unittest.TestCase):
    def test_identity_and_authors(self):
        _, meta = parse_article(article(), ARTICLES["stoneware-melt-2018"][1])
        self.assertEqual(meta["source_author"], "A Researcher")
        with self.assertRaisesRegex(ValueError, "IDENTITY"):
            parse_article(article(), "wrong-doi")

    def test_restricted_and_unknown_licenses_rejected(self):
        for license_path in ("by-nc/4.0", "by-nd/4.0", "by-nc-nd/4.0", "by/3.0", "by/4.0/extra"):
            with self.subTest(license_path=license_path):
                with self.assertRaisesRegex(ValueError, "LICENSE"):
                    parse_article(article(license_path), ARTICLES["stoneware-melt-2018"][1])

    def test_license_hostname_not_substring(self):
        raw = article().replace(b"creativecommons.org/", b"creativecommons.org.evil.example/")
        with self.assertRaisesRegex(ValueError, "LICENSE"):
            parse_article(raw, ARTICLES["stoneware-melt-2018"][1])

    def test_table_keeps_spans_empty_values_and_markup(self):
        doc, _ = parse_article(article(), ARTICLES["stoneware-melt-2018"][1])
        table = table_index(doc)[0]
        self.assertEqual(table["rows"][0][0]["colspan"], "2")
        self.assertEqual(table["rows"][1][0]["rowspan"], "2")
        self.assertIn("<sub>10</sub>", table["rows"][1][0]["xml"])
        self.assertEqual(table["rows"][1][1]["text"], "")
        self.assertIn("not measured", table["footnotes"])
        self.assertFalse(table["core_engine_eligible"])

    def test_immutable_reuse_and_path_guard(self):
        with tempfile.TemporaryDirectory() as root:
            immutable_write(root, "one/test", b"original")
            immutable_write(root, "one/test", b"original")
            with self.assertRaisesRegex(ValueError, "IMMUTABLE"):
                immutable_write(root, "one/test", b"changed")
            with self.assertRaisesRegex(ValueError, "PATH"):
                immutable_write(root, "../outside", b"x")

    def test_acquisition_replay_and_offline_integrity(self):
        with tempfile.TemporaryDirectory() as root, patch(
            "pipelines.ingestion.flow_sources.Collector.fetch", return_value=(article(), "https://www.ebi.ac.uk/test")
        ):
            path, first = run(root, ["stoneware-melt-2018"])
            _, second = run(root, ["stoneware-melt-2018"])
            self.assertEqual(first["counts"]["article_tables"], 1)
            self.assertTrue(second["files"][0]["reused"])
            self.assertEqual(first["files"][0]["sha256"], second["files"][0]["sha256"])
            self.assertEqual(verify_receipt(root, first)["verified_source_files"], 1)
            self.assertEqual(json.loads((Path(root) / path).read_text(encoding="utf-8"))["failures"], {})
            (Path(root) / first["files"][0]["readable_path"]).write_bytes(b"damaged")
            with self.assertRaisesRegex(ValueError, "CHECKSUM"):
                verify_receipt(root, first)

    def test_license_failure_does_not_publish_source(self):
        with tempfile.TemporaryDirectory() as root, patch(
            "pipelines.ingestion.flow_sources.Collector.fetch", return_value=(article("by-nc/4.0"), "https://www.ebi.ac.uk/test")
        ):
            _, receipt = run(root, ["stoneware-melt-2018"])
            self.assertEqual(receipt["counts"]["completed_sources"], 0)
            self.assertEqual(receipt["files"], [])
            self.assertIn("stoneware-melt-2018", receipt["failures"])

    def test_partial_download_not_counted_complete(self):
        license_raw = b"GlassPy is licensed under the GNU General Public Licence version 3"
        with tempfile.TemporaryDirectory() as root, patch(
            "pipelines.ingestion.flow_sources.Collector.fetch",
            side_effect=[(license_raw, "https://raw.githubusercontent.com/test"), OSError("network unavailable")]
        ):
            _, receipt = run(root, ["glasspy-model-reference"])
            self.assertEqual(len(receipt["files"]), 1)
            self.assertFalse(receipt["files"][0]["source_complete"])
            self.assertEqual(receipt["counts"]["completed_source_files"], 0)
            self.assertEqual(receipt["sources"], {})


if __name__ == "__main__":
    unittest.main()
