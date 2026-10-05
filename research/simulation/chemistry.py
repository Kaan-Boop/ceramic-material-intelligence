"""Deterministic chemistry bridge for generic simulation scenarios.

This bridge calculates a separate dry-batch chemistry report for each supplied
scenario layer. It does not calculate firing, melt, surface or defect results.
"""
from typing import Mapping

from research.chemistry.recipe import analyze_recipe
from research.material_resolver import MaterialResolutionError, resolve_engine_analysis


class ScenarioChemistryError(ValueError):
    """Raised when a scenario layer cannot be mapped to an exact recipe."""


def analyze_layer(
    *,
    layer_id: str,
    ingredients: list[dict],
    base_mass_g: float,
    scenario_materials: Mapping[str, Mapping[str, set[str]]],
) -> dict:
    """Analyze one layer using explicit parts and addition percentages.

    ``amount`` is a dry-base part for BASE rows and a percentage of the dry
    base for ADDITION rows. This is intentionally separate from scenario
    ``amount_g`` fields, which describe physical layer/material amounts.
    """
    if not ingredients:
        raise ScenarioChemistryError(f"EMPTY_LAYER_RECIPE: {layer_id}")
    layer_materials = scenario_materials.get(layer_id)
    if layer_materials is None:
        raise ScenarioChemistryError(f"LAYER_NOT_IN_SCENARIO: {layer_id}")
    if any(row["analysis_id"] not in layer_materials for row in ingredients):
        raise ScenarioChemistryError(f"RECIPE_MATERIAL_NOT_IN_LAYER: {layer_id}")
    analyses: dict[str, dict] = {}
    normalized: list[dict] = []
    for row in ingredients:
        analysis_id = row["analysis_id"]
        allowed = layer_materials[analysis_id]
        if row["role"] == "BASE" and not allowed.intersection({"BODY", "ENGOBE", "GLAZE", "OVERGLAZE"}):
            raise ScenarioChemistryError(f"ROLE_MAPPING_ERROR: {analysis_id}")
        if row["role"] == "ADDITION" and "ADDITION" not in allowed:
            raise ScenarioChemistryError(f"ROLE_MAPPING_ERROR: {analysis_id}")
        try:
            analyses[analysis_id] = resolve_engine_analysis(analysis_id)
        except MaterialResolutionError as exc:
            raise ScenarioChemistryError(str(exc)) from exc
        normalized.append({
            "analysis_id": analysis_id,
            "amount": row["amount"],
            "role": row["role"],
        })
    result = analyze_recipe(normalized, analyses, base_mass_g=base_mass_g)
    result["layer_id"] = layer_id
    result["layer_scope"] = "SCENARIO_LAYER_DRY_BATCH"
    result["limitations"] = [
        "Bu rapor yalnızca kuru baz oksit muhasebesidir.",
        "Pişirim, faz, erime, viskozite, yüzey ve kusur sonucu hesaplanmaz.",
        "BASE miktarları parça; ADDITION miktarları kuru baz yüzdesidir.",
    ]
    return result


def scenario_material_roles(scenario) -> dict[str, dict[str, set[str]]]:
    """Map scenario layer IDs to declared material roles."""
    layers = (scenario.body, *scenario.layers)
    return {
        layer.layer_id: {
            ref.analysis_id: {candidate.role for candidate in layer.materials if candidate.analysis_id == ref.analysis_id}
            for ref in layer.materials
        }
        for layer in layers
    }
