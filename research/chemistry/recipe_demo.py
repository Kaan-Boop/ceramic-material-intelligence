"""Run with python -m research.chemistry.recipe_demo. Synthetic, not a glaze recommendation."""
import json
from .foundation import formula_report
from .recipe import analyze_recipe


def demo():
    # Oxide accounting identities, NOT predictions of free phases after firing.
    definitions = {
        "ideal_k_feldspar": ("KAlSi3O8", {"K2O": .5, "Al2O3": .5, "SiO2": 3}, {}),
        "pure_silica": ("SiO2", {"SiO2": 1}, {}),
        "ideal_kaolinite": ("Al2Si2O5(OH)4", {"Al2O3": 1, "SiO2": 2}, {"H2O": 2}),
        "pure_calcite": ("CaCO3", {"CaO": 1}, {"CO2": 1}),
    }
    analyses = {}
    for key, (formula, oxides, volatile) in definitions.items():
        mass = formula_report(formula)["molar_mass_g_mol"]
        analyses[key] = {
            "version": "theoretical-v1", "source_ref": "project:ideal-formula-fixture/" + formula,
            "qualifier": "THEORETICAL_NOT_MANUFACTURER_ANALYSIS", "formula": formula,
            "complete": True, "omitted_oxides": "DECLARED_ZERO", "basis": "DRY", "loi_basis": "DRY",
            "loi_pct": sum(n * formula_report(o)["molar_mass_g_mol"] / mass * 100 for o, n in volatile.items()),
            "oxides": {o: n * formula_report(o)["molar_mass_g_mol"] / mass * 100 for o, n in oxides.items()},
        }
    ingredients = [{"analysis_id": key, "amount": amount, "role": "BASE"}
                   for key, amount in zip(definitions, (40, 25, 20, 15))]
    return analyze_recipe(ingredients, analyses)


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, ensure_ascii=False, allow_nan=False))
