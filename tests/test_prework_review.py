import unittest

from research.prework_review import review_attachment


def attachment(rows):
    return ("Some explanatory text\nconst RAW_MATERIALS = {\n" + rows + "\n};\n").encode()


class PreworkReviewTests(unittest.TestCase):
    def review(self, rows):
        return review_attachment(attachment(rows), reviewed_on="2026-09-26")

    def test_missing_mass_is_not_loi_or_normalized(self):
        r = self.review('whiting: { name: "Calcite", CaO: 56.1, MgO: 0.0 }')
        c = r["candidates"][0]
        self.assertEqual(c["reported_oxide_total"], 56.1)
        self.assertEqual(c["reported_oxides"], {"CaO": 56.1, "MgO": 0.0})
        self.assertNotIn("B2O3", c["reported_oxides"])
        self.assertIsNone(c["loi_pct"])
        self.assertEqual(c["attachment_line"], 3)
        self.assertEqual(r["counts"], dict(received=1, accepted=0, quarantined=1, rejected=0))

    def test_total_100_does_not_approve_source_or_training(self):
        r = self.review('silica: { name: "Silica", SiO2: 100 }')
        self.assertEqual(r["counts"]["accepted"], 0)
        self.assertEqual(r["training_permission"], "UNKNOWN_NOT_APPROVED")
        codes = {i["code"] for i in r["candidates"][0]["issues"]}
        self.assertTrue({"PURPOSE_NOT_ALLOWED", "ANALYSIS_BASIS_UNKNOWN"} <= codes)

    def test_malformed_executable_duplicate_and_nonfinite_stop(self):
        bad = [
            'a: { name: "A", SiO2: run() }',
            'a: { name: "A", SiO2: 1, SiO2: 2 }',
            'a: { name: "A", SiO2: 1e999 }',
            'a: { name: "A", SiO2: 2 }\na: { name: "B", SiO2: 3 }',
            'a: { name: "A", SiO2: 2 }; sideEffect();',
        ]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.review(value)

    def test_invalid_percentage_rejected_not_silently_fixed(self):
        for value in (-1, 101):
            r = self.review(f'a: {{ name: "A", SiO2: {value} }}')
            self.assertEqual(r["counts"]["rejected"], 1)
            self.assertEqual(r["candidates"][0]["reported_oxides"]["SiO2"], value)

    def test_unknown_oxide_is_review_issue(self):
        r = self.review('a: { name: "A", XxO: 2 }')
        self.assertIn("UNSUPPORTED_OXIDE", {i["code"] for i in r["candidates"][0]["issues"]})

    def test_numeric_boundaries_preserve_literals_and_do_not_overflow(self):
        for value in ("-1e-999", "1e-999"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "NUMERIC_UNDERFLOW"):
                self.review(f'a: {{ name: "A", SiO2: {value} }}')
        r = self.review('a: { name: "A", SiO2: 100.00000000000000001 }')
        self.assertEqual(r["counts"]["rejected"], 1)
        self.assertEqual(r["candidates"][0]["reported_numeric_literals"]["SiO2"], "100.00000000000000001")
        self.assertIsNone(r["candidates"][0]["reported_oxide_total"])
        r = self.review('a: { name: "A", SiO2: 1e308, CaO: 1e308 }')
        self.assertEqual(r["counts"]["rejected"], 1)
        self.assertIsNone(r["candidates"][0]["reported_oxide_total"])

    def test_missing_or_ambiguous_block_stops(self):
        for raw in (b"no material block", attachment("") , attachment('a: { name: "A", SiO2: 1 }') * 2):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                review_attachment(raw, reviewed_on="2026-09-26")

    def test_repeatability_and_hash_covers_whole_attachment(self):
        raw = attachment('a: { name: "A", SiO2: 1 }')
        r = review_attachment(raw, reviewed_on="2026-09-26")
        self.assertEqual(r, review_attachment(raw, reviewed_on="2026-09-26"))
        self.assertNotEqual(r["attachment_sha256"], review_attachment(raw + b"\n", reviewed_on="2026-09-26")["attachment_sha256"])
        self.assertFalse(r["source_code_executed"])
        self.assertFalse(r["production_data_changed"])


if __name__ == "__main__":
    unittest.main()
