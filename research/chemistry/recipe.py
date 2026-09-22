"""Strict dry-batch research calculator; no phase or firing predictions."""
from copy import deepcopy
import math

from .foundation import ChemistryInputError, OXIDES, digest, formula_report, nonnegative

VERSION = "recipe-research/0.1.0"
FLUX = ("Li2O", "Na2O", "K2O", "MgO", "CaO", "SrO", "BaO", "ZnO")
CONVENTION = "standard-flux-v1"


def analyze_recipe(ingredients, analyses, *, base_mass_g=100.0):
    """BASE amounts are parts; ADDITION amounts are percent of dry base.

    Analyses require explicit completeness/omitted-zero declarations. DRY oxide
    percentages include LOI in their denominator; IGNITED percentages exclude it.
    Both require LOI referred to DRY mass. No moisture conversion is inferred.
    """
    if not isinstance(ingredients, list) or not 1 <= len(ingredients) <= 100:
        raise ChemistryInputError("INGREDIENTS_1_TO_100_REQUIRED")
    if not isinstance(analyses, dict):
        raise ChemistryInputError("ANALYSIS_MAP_REQUIRED")
    base_mass_g = nonnegative(base_mass_g)
    if base_mass_g == 0:
        raise ChemistryInputError("ZERO_BASE_MASS")
    amounts = []
    for row in ingredients:
        if not isinstance(row, dict) or row.get("role") not in ("BASE", "ADDITION"):
            raise ChemistryInputError("EXPLICIT_INGREDIENT_ROLE_REQUIRED")
        if not isinstance(row.get("analysis_id"), str) or row["analysis_id"] not in analyses:
            raise ChemistryInputError("UNKNOWN_ANALYSIS")
        amounts.append(nonnegative(row.get("amount")))
    total = math.fsum(a for r, a in zip(ingredients, amounts) if r["role"] == "BASE")
    if total == 0:
        raise ChemistryInputError("ZERO_BASE_TOTAL")
    masses, losses, normalized, snapshots = {}, [], [], {}
    for row, amount in zip(ingredients, amounts):
        key = row["analysis_id"]
        analysis = analyses[key]
        if not isinstance(analysis, dict):
            raise ChemistryInputError("ANALYSIS_OBJECT_REQUIRED")
        if analysis.get("complete") is not True or analysis.get("omitted_oxides") != "DECLARED_ZERO":
            raise ChemistryInputError("INCOMPLETE_ANALYSIS")
        if not analysis.get("version") or not analysis.get("source_ref"):
            raise ChemistryInputError("ANALYSIS_PROVENANCE_REQUIRED")
        basis = analysis.get("basis")
        if basis not in ("DRY", "IGNITED") or analysis.get("loi_basis") != "DRY":
            raise ChemistryInputError("UNSUPPORTED_OR_UNKNOWN_BASIS")
        loi = nonnegative(analysis.get("loi_pct"))
        if loi >= 100:
            raise ChemistryInputError("LOI_MUST_BE_LESS_THAN_100")
        oxides = analysis.get("oxides")
        if not isinstance(oxides, dict) or not oxides or set(oxides) - set(OXIDES):
            raise ChemistryInputError("SUPPORTED_OXIDE_MAP_REQUIRED")
        weights = {o: nonnegative(w) for o, w in oxides.items()}
        closure = math.fsum(weights.values()) + (loi if basis == "DRY" else 0)
        # Deliberately strict research scope: no rounding repair or silent closure.
        if abs(closure - 100) > 1e-6:
            raise ChemistryInputError("ANALYSIS_NOT_CLOSED_NO_SILENT_NORMALIZATION")
        fraction = amount / total if row["role"] == "BASE" else amount / 100
        dry_mass = nonnegative(base_mass_g * fraction)
        retained = 1 - loi / 100 if basis == "IGNITED" else 1
        for oxide, weight in weights.items():
            masses.setdefault(oxide, []).append(dry_mass * retained * weight / 100)
        losses.append(dry_mass * loi / 100)
        normalized.append({**deepcopy(row), "original_amount": amount,
                           "percent_of_base": fraction * 100, "dry_mass_g": dry_mass})
        snapshots[key] = deepcopy(analysis)
    oxide_mass = {o: math.fsum(v) for o, v in sorted(masses.items())}
    reports = {o: formula_report(o, m) for o, m in oxide_mass.items()}
    moles = {o: r["amount_mol"] for o, r in reports.items()}
    mole_total = math.fsum(moles.values())
    flux_total = math.fsum(moles.get(o, 0) for o in FLUX)
    oxide_total = math.fsum(oxide_mass.values())
    if oxide_total <= 0 or mole_total <= 0:
        raise ChemistryInputError("NUMERICAL_UNDERFLOW_OR_ZERO_RETAINED_OXIDES")

    def ratio(numerator, denominator):
        return {"status": "AVAILABLE" if denominator else "UNAVAILABLE",
                "value": numerator / denominator if denominator else None,
                "unavailable_reason": None if denominator else "ZERO_DENOMINATOR"}

    alkali = math.fsum(moles.get(o, 0) for o in FLUX[:3])
    ro = math.fsum(moles.get(o, 0) for o in FLUX[3:])
    first = next(iter(reports.values()))
    inputs = {"ingredients": deepcopy(ingredients), "analyses": snapshots, "base_mass_g": base_mass_g}
    return {"schema_version": "1", "engine_version": VERSION,
            "evidence_kind": "CALCULATED", "method_kind": "DETERMINISTIC",
            "qualifier": "THEORETICAL_OXIDE_ACCOUNTING", "input_snapshot": inputs,
            "constant_set_id": first["constant_set_id"], "constant_set_sha256": first["constant_set_sha256"],
            "umf_convention": CONVENTION,
            "input_hash": digest({"inputs": inputs, "engine": VERSION, "convention": CONVENTION,
                                  "constants": first["constant_set_sha256"]}),
            "normalized_ingredients": normalized, "oxide_mass_g": oxide_mass,
            "oxide_moles": moles, "oxide_mol_pct": {o: n / mole_total * 100 for o, n in moles.items()},
            "retained_oxide_wt_pct": {o: m / oxide_total * 100 for o, m in oxide_mass.items()},
            "loi_mass_g": math.fsum(losses), "retained_oxide_mass_g": oxide_total,
            "total_dry_batch_mass_g": math.fsum(r["dry_mass_g"] for r in normalized),
            "umf": {"status": "AVAILABLE" if flux_total else "UNAVAILABLE",
                    "unavailable_reason": None if flux_total else "ZERO_FLUX_MOLES",
                    "values": {o: n / flux_total for o, n in moles.items()} if flux_total else None},
            "flux_distribution": {o: moles.get(o, 0) / flux_total for o in FLUX} if flux_total else None,
            "ratios": {"SiO2_to_Al2O3_molar": ratio(moles.get("SiO2", 0), moles.get("Al2O3", 0)),
                       "atomic_Si_to_Al": ratio(moles.get("SiO2", 0), 2 * moles.get("Al2O3", 0)),
                       "RO_to_R2O": ratio(ro, alkali)},
            "warnings": ["Dry input masses only; declared-zero omissions are an explicit input assumption",
                         "LOI is a mass budget, not gas identity, release temperature or reaction rate",
                         "Oxide equivalents are not actual phases; redox and volatilization are not simulated",
                         "Pinned constants are not the latest CIAAW table; see foundation audit"],
            "predictions": {"status": "UNAVAILABLE", "reason": "No validated firing/surface/defect model"}}
