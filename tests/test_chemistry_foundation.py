import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    import periodictable
except ImportError:
    periodictable = None

if periodictable is not None:
    from research.chemistry.foundation import (ChemistryInputError, element_catalog, atom_counts,
        formula_report, oxide_equivalent, reaction_balance, OXIDES)
    from research.chemistry.__main__ import run


@unittest.skipIf(periodictable is None, "Install reviewed chemistry research lock; do not count skipped tests as validation")
class ChemistryTests(unittest.TestCase):
    def test_all_element_identities_unique_and_complete(self):
        rows = element_catalog()
        self.assertEqual([x["atomic_number"] for x in rows], list(range(1, 119)))
        self.assertEqual(len({x["symbol"] for x in rows}), 118)
        self.assertTrue(all(x["source_url"] and x["constant_set_id"] for x in rows))

    def test_nonstandard_masses_are_not_nominal_isotopes(self):
        rows = {r["symbol"]: r for r in element_catalog()}
        for name in ("Tc", "Pm", "Og"):
            self.assertIsNone(rows[name]["selected_molar_mass_g_mol"])
            with self.assertRaisesRegex(ChemistryInputError, "STANDARD_MASS_UNAVAILABLE"):
                formula_report(name)

    def test_formula_counts_and_parentheses(self):
        self.assertEqual(atom_counts("Al2Si2O5(OH)4"), {"Al": 2, "Si": 2, "O": 9, "H": 4})
        self.assertEqual(atom_counts("CaMg(CO3)2"), {"Ca": 1, "Mg": 1, "C": 2, "O": 6})
        self.assertEqual(atom_counts("Al2(SO4)3"), {"Al": 2, "S": 3, "O": 12})

    def test_hand_silica_molar_mass(self):
        result = formula_report("SiO2", 60.083)
        self.assertAlmostEqual(result["molar_mass_g_mol"], 28.085 + 2 * 15.999, places=12)
        self.assertAlmostEqual(result["amount_mol"], 1, places=12)

    def test_all_oxide_element_mass_balances(self):
        for formula in OXIDES:
            with self.subTest(formula=formula):
                result = formula_report(formula, 37.2)
                self.assertAlmostEqual(sum(result["element_mass_g"].values()), 37.2, places=11)
                # Library parser cross-check, not an independent experimental validation.
                self.assertAlmostEqual(result["molar_mass_g_mol"], periodictable.formula(formula).mass, places=10)

    def test_invalid_or_unsupported_formulas(self):
        for formula in ("", None, "SiO0", "SiO-2", "2SiO2", "SiO2@2.65", "CuSO4.5H2O",
                        "Fe{2+}", "[13]C", "D2O", "XxO2", "()", "(SiO2", "SiO2)",
                        "Si10000", "Ca0.5Mg0.5O", "SiO2 " , "(" * 9 + "Si" + ")" * 9):
            with self.subTest(formula=formula), self.assertRaises(ChemistryInputError):
                formula_report(formula)

    def test_amount_validation(self):
        for amount in (-1, True, "2", None, float("nan"), float("inf"), 10**400):
            with self.subTest(amount=str(amount)[:20]), self.assertRaises(ChemistryInputError):
                formula_report("SiO2", amount)
        self.assertEqual(formula_report("SiO2", 0)["amount_mol"], 0)

    def test_package_version_guard(self):
        with patch("research.chemistry.foundation.version", return_value="99.0"):
            with self.assertRaisesRegex(ChemistryInputError, "UNREVIEWED"):
                element_catalog()

    def test_replay_and_scale(self):
        a = formula_report("SiO2", 10)
        self.assertEqual(a, formula_report("SiO2", 10))
        b = formula_report("SiO2", 20)
        self.assertNotEqual(a["input_hash"], b["input_hash"])
        self.assertEqual(2 * a["amount_mol"], b["amount_mol"])

    def test_explicit_iron_equivalence_not_redox_prediction(self):
        ferrous = oxide_equivalent("Fe", 10, "FeO")
        ferric = oxide_equivalent("Fe", 10, "Fe2O3")
        self.assertGreater(ferric["oxide_equivalent_g"], ferrous["oxide_equivalent_g"])
        self.assertAlmostEqual(ferric["oxide_equivalent_g"], 10 * (2 * 55.845 + 3 * 15.999) / (2 * 55.845))
        self.assertEqual(ferric["qualifier"], "ASSUMED_REPORTING_BASIS")

    def test_wrong_oxide_equivalence_rejected(self):
        for element, formula in (("Ca", "FeO"), ("O", "FeO"), ("Ca", "CaCO3"), ("Fe", "Fe")):
            with self.subTest(element=element, formula=formula), self.assertRaises(ChemistryInputError):
                oxide_equivalent(element, 10, formula)

    def test_balanced_equation_no_physical_prediction(self):
        r = reaction_balance({"CaCO3": 1}, {"CaO": 1, "CO2": 1})
        self.assertTrue(r["balanced"])
        self.assertEqual(r["physical_reaction"]["status"], "UNAVAILABLE")
        self.assertFalse(reaction_balance({"FeO": 1}, {"Fe2O3": 1})["balanced"])

    def test_invalid_reaction(self):
        for side in ({}, {"CaO": -1}, {"CaO": True}, {"CaO": 1.5}, []):
            with self.subTest(side=side), self.assertRaises(ChemistryInputError):
                reaction_balance(side, {"CaO": 1})

    def test_exports_are_separate_and_receipted(self):
        with tempfile.TemporaryDirectory() as directory:
            a, result = run(directory)
            b, _ = run(directory)
            self.assertNotEqual(a, b)
            self.assertEqual(result["element_count"], 118)
            self.assertEqual(result["oxide_count"], len(OXIDES))
            for filename, checksum in result["files"].items():
                self.assertEqual(hashlib.sha256((a / filename).read_bytes()).hexdigest(), checksum)
            self.assertEqual(json.loads((a / "receipt.json").read_text())["files"], result["files"])
