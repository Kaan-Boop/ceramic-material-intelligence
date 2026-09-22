import copy
import unittest

from research.chemistry.foundation import ChemistryInputError
from research.chemistry.recipe import analyze_recipe


def analysis(oxides, loi=0, basis="DRY"):
    return dict(version="synthetic-v1", source_ref="synthetic:unit-test-not-manufacturer",
                complete=True, omitted_oxides="DECLARED_ZERO", basis=basis,
                loi_basis="DRY", loi_pct=loi, oxides=oxides)


def ingredient(key, amount, role="BASE"):
    return dict(analysis_id=key, amount=amount, role=role)


class RecipeResearchTests(unittest.TestCase):
    def setUp(self):
        self.analyses = {"silica": analysis({"SiO2": 100}), "lime": analysis({"CaO": 100}),
                         "alumina": analysis({"Al2O3": 100})}
        # Independent hand molar masses with the selected constant table.
        self.rows = [ingredient("silica", 60.083 * 3), ingredient("lime", 56.077),
                     ingredient("alumina", 101.9600768 * .5)]

    def test_hand_umf_and_distinct_atomic_ratio(self):
        result = analyze_recipe(self.rows, self.analyses)
        self.assertAlmostEqual(result["umf"]["values"]["SiO2"], 3, places=7)
        self.assertAlmostEqual(result["umf"]["values"]["Al2O3"], .5, places=7)
        self.assertAlmostEqual(result["ratios"]["SiO2_to_Al2O3_molar"]["value"], 6, places=7)
        self.assertAlmostEqual(result["ratios"]["atomic_Si_to_Al"]["value"], 3, places=7)
        self.assertAlmostEqual(sum(result["flux_distribution"].values()), 1)

    def test_parts_scaling_and_order_invariance(self):
        a = analyze_recipe(self.rows, self.analyses)
        b = analyze_recipe([{**r, "amount": r["amount"] * 9} for r in reversed(self.rows)], self.analyses)
        for o in a["oxide_mass_g"]:
            self.assertAlmostEqual(a["oxide_mass_g"][o], b["oxide_mass_g"][o])

    def test_addition_is_not_renormalized_into_base(self):
        r = analyze_recipe([ingredient("silica", 95), ingredient("lime", 2, "ADDITION")], self.analyses)
        self.assertEqual(r["total_dry_batch_mass_g"], 102)
        self.assertEqual(r["oxide_mass_g"], {"CaO": 2, "SiO2": 100})

    def test_dry_and_ignited_equivalence_no_double_loi(self):
        data = {"dry": analysis({"CaO": 60}, 40), "ignited": analysis({"CaO": 100}, 40, "IGNITED")}
        for key in data:
            r = analyze_recipe([ingredient(key, 100)], data)
            self.assertEqual(r["oxide_mass_g"]["CaO"], 60)
            self.assertEqual(r["loi_mass_g"], 40)
            self.assertEqual(r["retained_oxide_mass_g"] + r["loi_mass_g"], 100)

    def test_zero_flux_and_ratio_are_unavailable(self):
        r = analyze_recipe([ingredient("silica", 1)], self.analyses)
        self.assertEqual(r["umf"]["status"], "UNAVAILABLE")
        self.assertIsNone(r["ratios"]["atomic_Si_to_Al"]["value"])

    def test_batch_scaling(self):
        a = analyze_recipe(self.rows, self.analyses)
        b = analyze_recipe(self.rows, self.analyses, base_mass_g=1000)
        for o in a["oxide_mass_g"]:
            self.assertAlmostEqual(b["oxide_mass_g"][o], a["oxide_mass_g"][o] * 10)
            self.assertAlmostEqual(b["umf"]["values"][o], a["umf"]["values"][o])

    def test_replay_and_snapshot_isolation(self):
        a = analyze_recipe(self.rows, self.analyses)
        snap = a["input_snapshot"]
        self.assertEqual(a, analyze_recipe(**snap))
        self.analyses["silica"]["oxides"]["SiO2"] = 90
        self.assertEqual(snap["analyses"]["silica"]["oxides"]["SiO2"], 100)

    def test_invalid_analysis_is_not_silently_repaired(self):
        for updates in ({"basis": "UNKNOWN"}, {"basis": "AS_RECEIVED"}, {"complete": False},
                        {"omitted_oxides": "UNKNOWN"}, {"source_ref": None}, {"loi_pct": -1},
                        {"loi_pct": 100}, {"loi_basis": "AS_RECEIVED"}, {"oxides": {"SiO2": 99}},
                        {"oxides": {"XxO2": 100}}, {"oxides": {"SiO2": float("nan")}}):
            data = copy.deepcopy(self.analyses)
            data["silica"].update(updates)
            with self.subTest(updates=updates), self.assertRaises(ChemistryInputError):
                analyze_recipe([ingredient("silica", 1)], data)

    def test_bad_amount_and_zero_total(self):
        for value in (-1, 0, True, "1", float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ChemistryInputError):
                analyze_recipe([ingredient("silica", value)], self.analyses)

    def test_unknown_material_and_role(self):
        for row in (ingredient("unknown", 1), ingredient("silica", 1, "UNKNOWN")):
            with self.assertRaises(ChemistryInputError):
                analyze_recipe([row], self.analyses)

    def test_demo_closure_and_not_manufacturer_data(self):
        from research.chemistry.recipe_demo import demo
        result = demo()
        self.assertAlmostEqual(result["retained_oxide_mass_g"] + result["loi_mass_g"], 100)
        self.assertAlmostEqual(result["umf"]["values"]["CaO"] + result["umf"]["values"]["K2O"], 1)
        self.assertTrue(all(a["qualifier"] == "THEORETICAL_NOT_MANUFACTURER_ANALYSIS"
                            for a in result["input_snapshot"]["analyses"].values()))

    def test_underflow_is_controlled(self):
        with self.assertRaisesRegex(ChemistryInputError, "NUMERICAL_UNDERFLOW"):
            analyze_recipe([ingredient("silica", 1)], self.analyses, base_mass_g=5e-324)


if __name__ == "__main__":
    unittest.main()
