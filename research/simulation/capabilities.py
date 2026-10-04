"""Capability gating for generic simulation scenarios.

This module deliberately reports what the current release can support; it does
not synthesize missing material properties or turn a requested output into a
probability. The caller may pass a resolved property inventory keyed by
``analysis_id``. Values are property names known to be available, for example
``{"oxide_analysis", "density"}``.
"""
from collections.abc import Mapping
from typing import Literal

from .scenario import SimulationScenario


Status = Literal["AVAILABLE", "PARTIAL", "UNAVAILABLE"]


def _material_ids(scenario: SimulationScenario) -> tuple[str, ...]:
    refs = [*scenario.body.materials]
    for layer in scenario.layers:
        refs.extend(layer.materials)
    # Preserve first-seen order while allowing a material to be used in more
    # than one layer without double-counting its property requirements.
    return tuple(dict.fromkeys(ref.analysis_id for ref in refs))


def _has_all(properties: Mapping[str, set[str]], ids: tuple[str, ...], required: set[str]) -> bool:
    return all(required.issubset(properties.get(material_id, set())) for material_id in ids)


def assess_capabilities(
    scenario: SimulationScenario,
    property_inventory: Mapping[str, set[str]] | None = None,
) -> dict:
    """Return explicit status for each requested output.

    The inventory is intentionally an input rather than a database lookup so
    the result remains replayable and can be attached to an immutable run.
    ``AVAILABLE`` means the release has a method *and* the required inputs;
    ``PARTIAL`` means only a limited intermediate is available.
    """
    inventory = property_inventory or {}
    ids = _material_ids(scenario)
    has_chemistry = _has_all(inventory, ids, {"oxide_analysis"})
    has_thermal = _has_all(inventory, ids, {"density", "specific_heat", "conductivity"})
    body_ids = tuple(ref.analysis_id for ref in scenario.body.materials)
    coating_ids = tuple(
        ref.analysis_id
        for layer in scenario.layers
        if layer.layer_id != "body"
        for ref in layer.materials
        if ref.role in {"GLAZE", "OVERGLAZE", "ENGOBE"}
    )
    has_cte = bool(coating_ids) and all("cte" in inventory.get(material_id, set()) for material_id in (*body_ids, *coating_ids))
    output_status: dict[str, dict] = {}
    for output in scenario.target.requested_outputs:
        if output in {"normalized_recipe", "oxide_composition", "umf"}:
            status: Status = "AVAILABLE" if has_chemistry else "UNAVAILABLE"
            reason = "Resolved oxide analyses are available." if has_chemistry else "Every referenced material needs a versioned oxide analysis."
            method = "DETERMINISTIC"
            evidence = "CALCULATED"
        elif output in {"firing_timeline", "planned_duration"}:
            status, reason, method, evidence = "AVAILABLE", "Only the planned schedule is calculated; kiln/sample temperature is not measured.", "DETERMINISTIC", "CALCULATED"
        elif output == "heat_transfer":
            status = "AVAILABLE" if has_thermal else "UNAVAILABLE"
            reason = "Resolved thermal properties and geometry are available." if has_thermal else "Density, specific heat and conductivity for every layer are required; no defaults are inferred."
            method, evidence = "DETERMINISTIC", "PREDICTED"
        elif output == "fit_risk":
            status = "PARTIAL" if has_cte else "UNAVAILABLE"
            reason = "CTE comparison is available as an estimated indicator, not a crack probability." if has_cte else "Measured or explicitly estimated body and glaze CTE inputs are required."
            method, evidence = "DETERMINISTIC", "PREDICTED"
        elif output in {"melt_fraction", "viscosity", "reaction_kinetics", "surface_state", "color", "defect_risk"}:
            status, reason, method, evidence = "UNAVAILABLE", "No validated composition- and temperature-dependent model is released for this output.", "UNAVAILABLE", "PREDICTED"
        else:
            status, reason, method, evidence = "UNAVAILABLE", "Output is not part of the current simulation contract.", "UNAVAILABLE", "PREDICTED"
        output_status[output] = {
            "status": status,
            "evidence_kind": evidence,
            "method_kind": method,
            "reason": reason,
        }

    return {
        "schema_version": "simulation-capabilities-v1",
        "scenario_id": scenario.scenario_id,
        "input_hash": scenario.input_hash(),
        "material_ids": list(ids),
        "outputs": output_status,
        "limitations": [
            "Capability status is not a physical result or confidence interval.",
            "Missing properties remain unavailable; the assessor never fills them from material names.",
        ],
    }
