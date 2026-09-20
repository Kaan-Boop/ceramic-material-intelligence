import unittest
from unittest.mock import patch
from pipelines.ingestion.acquire import ReviewedRedirects
from pipelines.ingestion.profile_research import reported_cell, profile_csv, uci_records


class ResearchTests(unittest.TestCase):
    def test_ranges_not_midpoints(self):
        value = reported_cell("30–40")
        self.assertEqual(value["lower"], "30")
        self.assertIsNone(value["value"])

    def test_dash_not_zero(self):
        self.assertIsNone(reported_cell("-")["value"])
        self.assertEqual(reported_cell("0")["value"], "0")

    def test_censored_not_exact(self):
        self.assertIsNone(reported_cell("<1")["value"])
        self.assertEqual(reported_cell("<1")["upper_exclusive"], "1")

    def test_unknown_syntax_fails(self):
        with self.assertRaises(ValueError):
            reported_cell("trace")

    def test_csv_missing_and_duplicate(self):
        result = profile_csv(b'id,value\na,\na,\n')
        self.assertEqual(result["profile"]["blank_cells"], 2)
        self.assertEqual(result["profile"]["exact_duplicate_nonempty_rows"], 1)

    def test_quoted_csv(self):
        result = profile_csv(b'name,amount\n"a,b",3.1\n')
        self.assertEqual(result["rows"][1], ["a,b", "3.1"])

    def test_uci_unit_conversion_negative_preserved(self):
        head = "Ceramic Name,Part,Na2O,MgO,Al2O3,SiO2,K2O,CaO,TiO2,Fe2O3,MnO,CuO,ZnO,PbO2,Rb2O,SrO,Y2O3,ZrO2,P2O5\n"
        row = "S1,Body,1,1,1,1,1,1,1,1,500,1,1,1,1,-10,1,1,1\n"
        _, records = uci_records((head + row).encode())
        measures = {v["reported_as"]: v for v in records[0]["measurements"]}
        self.assertEqual(measures["MnO"]["wt_pct"], "0.05")
        self.assertEqual(measures["Na2O"]["wt_pct"], "1")
        self.assertEqual(measures["SrO"]["reported_value"], "-10")
        self.assertIsNone(measures["SrO"]["wt_pct"])
        self.assertFalse(records[0]["core_engine_eligible"])

    def test_schema_change_stops_uci(self):
        with self.assertRaisesRegex(ValueError, "UCI_SCHEMA_CHANGED"):
            uci_records(b'a,b\n1,2\n')

    def test_redirect_checks_before_following(self):
        with self.assertRaisesRegex(ValueError, "UNREVIEWED_DOWNLOAD_HOST"):
            ReviewedRedirects().redirect_request(None, None, 302, "", {}, "https://example.com/private")


if __name__ == "__main__":
    unittest.main()
