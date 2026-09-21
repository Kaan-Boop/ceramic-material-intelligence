"""Local JSON adapter: python -m research.thermal INPUT --output NEW_FILE."""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

from .core import Curve, Scenario, ModelInputError, MODEL_VERSION, calculate, sensitivity

SOURCES = [
    "https://mooseframework.inl.gov/source/materials/ComputeInstantaneousThermalExpansionFunctionEigenstrain.html",
    "https://bleyerj.github.io/comet-fenicsx/tours/linear_problems/thermoelasticity_weak/thermoelasticity_weak.html",
]


def exact_fields(data, fields, field):
    if not isinstance(data, dict) or set(data) != set(fields):
        raise ModelInputError("SCHEMA_FIELDS_MISMATCH", field)


def read_curve(data):
    exact_fields(data, ("material_id", "source_ref", "data_kind", "points", "coefficient_kind", "unit"), "curve")
    points = data["points"]
    if not isinstance(points, list) or any(not isinstance(p, list) or len(p) != 2 for p in points):
        raise ModelInputError("INVALID_POINT", "points")
    return Curve(**{**data, "points": tuple(tuple(p) for p in points)})


def run(data):
    exact_fields(data, ("schema_version", "glaze", "body", "reference_temperature_c",
                       "target_temperature_c", "reference_length_mm", "sensitivity_steps"), "scenario")
    if data["schema_version"] != "thermal-scenario/1":
        raise ModelInputError("UNSUPPORTED_SCHEMA", "schema_version")
    scenario = Scenario(read_curve(data["glaze"]), read_curve(data["body"]),
                        data["reference_temperature_c"], data["target_temperature_c"],
                        data["reference_length_mm"])
    values = calculate(scenario)
    rows = sensitivity(scenario, data["sensitivity_steps"])
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return {
        "schema_version": "thermal-report/1", "model_version": MODEL_VERSION,
        "input_hash": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        "input_snapshot": asdict(scenario), "sensitivity_steps": dict(data["sensitivity_steps"]),
        "source_refs": SOURCES,
        "evidence_kind": "PREDICTED", "method_kind": "DETERMINISTIC",
        "qualifier": "THEORETICAL", "status": "AVAILABLE",
        "contains_synthetic_inputs": any(c.data_kind == "SYNTHETIC" for c in (scenario.glaze, scenario.body)),
        "uncertainty": None, "uncertainty_reason": "INPUT_DISTRIBUTIONS_AND_MODEL_ERROR_NOT_ESTABLISHED",
        "value_units": {key: "mm" if key.endswith("_mm") else "1" for key in values},
        "values": values, "sensitivity_oat": rows,
        "unavailable_sections": {
            "stress": "NO_BONDED_LAYER_MECHANICS_OR_RELAXATION_MODEL",
            "failure_probability": "NO_VALIDATED_FRACTURE_MODEL_OR_EXPERIMENTAL_CALIBRATION",
            "chemical_reactions": "NO_THERMODYNAMIC_DATABASE_OR_KINETICS_MODEL",
            "cooling_rate_effect": "MODEL_DEPENDS_ON_TEMPERATURE_ONLY",
        },
        "limitations": [
            "Free contraction difference is NOT the displacement of a bonded object.",
            "Reference temperature is a chosen baseline, NOT measured stress-free or glass-transition temperature.",
            "Small-strain, isotropic, reversible model; no sintering, phase changes or temperature gradients.",
            "No extrapolation, mean-CTE conversion or automatic chemistry-to-CTE inference.",
            "Sensitivity steps are scenario choices, NOT measured uncertainties or confidence intervals.",
            "Input provenance is recorded but NOT independently authenticated by this prototype.",
        ],
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ModelInputError("DUPLICATE_JSON_KEY", key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        report = json.dumps(run(data), ensure_ascii=False, allow_nan=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(report + "\n")
            print(str(args.output.resolve()))
        else:
            print(report)
        return 0
    except (ModelInputError, OSError, ValueError) as exc:
        print(json.dumps({"status": "UNAVAILABLE", "error": str(exc),
                          "code": getattr(exc, "code", "INPUT_OR_OUTPUT_ERROR")}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
