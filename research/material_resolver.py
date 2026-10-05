"""Exact material-analysis resolution for simulation requests.

Names are presentation data only. A simulation may use a material only when
its exact local record is present; research-only records remain visible but do
not silently become chemistry inputs.
"""
from functools import lru_cache

from research.chemistry.recipe_demo import demo
from research.material_library import build_library


class MaterialResolutionError(ValueError):
    """Raised when a requested analysis id cannot be resolved exactly."""


@lru_cache(maxsize=1)
def library_snapshot() -> tuple[dict, ...]:
    input_snapshot = demo()["input_snapshot"]
    theoretical = [
        {
            "analysis_id": key,
            "name": analysis.get("name", key),
            "formula": analysis["formula"],
            "version": analysis["version"],
            "qualifier": analysis["qualifier"],
            "basis": analysis["basis"],
            "loi_pct": analysis["loi_pct"],
            "oxides": analysis["oxides"],
            "source_ref": analysis["source_ref"],
            "source_url": "project:theoretical-fixture",
        }
        for key, analysis in input_snapshot["analyses"].items()
    ]
    return tuple(build_library(theoretical))


def resolve_material(analysis_id: str) -> dict:
    for record in library_snapshot():
        if record["id"] == analysis_id:
            return dict(record)
    raise MaterialResolutionError(f"UNKNOWN_MATERIAL_ANALYSIS: {analysis_id}")


def resolve_materials(analysis_ids: tuple[str, ...] | list[str]) -> tuple[list[dict], dict[str, set[str]]]:
    """Return records and server-derived property availability.

    The returned property inventory is deliberately narrow: an analysis is
    available to the chemistry engine only when its record is explicitly marked
    ``engine_eligible`` and has oxide values. Other properties are not inferred.
    """
    records = []
    inventory: dict[str, set[str]] = {}
    seen: set[str] = set()
    for analysis_id in analysis_ids:
        if analysis_id in seen:
            continue
        seen.add(analysis_id)
        record = resolve_material(analysis_id)
        records.append(record)
        properties: set[str] = set()
        if record.get("engine_eligible") and record.get("oxides"):
            properties.add("oxide_analysis")
        inventory[analysis_id] = properties
    return records, inventory
