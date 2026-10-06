"""Observed-versus-calculated outcome linking for fired specimens.

This module deliberately compares only directly comparable quantities. It is
not a model trainer, a defect predictor, or a pass/fail certification tool.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import math
import statistics
from typing import Mapping, Sequence

from research.chemistry.foundation import digest


VERSION = "observed-outcome-validation/0.1.0"

# Only quantities with an explicit counterpart in the current deterministic
# outcome indicators are allowed. A glaze edge distance, for example, is not
# silently compared with the ideal-film travel indicator.
OBSERVABLES = {
    "gloss_mean_gu": {
        "section": "gloss",
        "value_key": "mean_gu",
        "unit": "GU",
        "low": 0.0,
        "high": 2000.0,
    },
    "water_absorption_mass_pct": {
        "section": "porosity",
        "value_key": "water_absorption_mass_pct",
        "unit": "%",
        "low": 0.0,
        "high": 1000.0,
    },
    "apparent_open_porosity_volume_pct": {
        "section": "porosity",
        "value_key": "apparent_open_porosity_volume_pct",
        "unit": "%",
        "low": 0.0,
        "high": 100.0,
    },
}


class ExperimentValidationError(ValueError):
    """An observation cannot be compared without changing its meaning."""


def _text(record: Mapping, key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > 500:
        raise ExperimentValidationError(f"MISSING_PROVENANCE:{key}")
    return value.strip()


def _number(record: Mapping, key: str, low: float, high: float) -> float:
    value = record.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ExperimentValidationError(f"INVALID_NUMBER:{key}")
    if not low <= value <= high:
        raise ExperimentValidationError(f"OUT_OF_RANGE:{key}")
    return float(value)


def _validate_observation(record: Mapping) -> dict:
    required = {"observable", "value", "unit", "specimen_id", "source_ref", "method", "status"}
    if not isinstance(record, Mapping) or set(record) != required:
        raise ExperimentValidationError("INVALID_OBSERVATION_FIELDS")
    observable = record.get("observable")
    definition = OBSERVABLES.get(observable)
    if definition is None:
        raise ExperimentValidationError("UNSUPPORTED_OBSERVABLE")
    if record.get("unit") != definition["unit"]:
        raise ExperimentValidationError("UNIT_MISMATCH")
    if record.get("status") not in {"MEASURED", "REPORTED"}:
        raise ExperimentValidationError("INVALID_OBSERVATION_STATUS")
    return {
        "observable": observable,
        "value": _number(record, "value", definition["low"], definition["high"]),
        "unit": definition["unit"],
        "specimen_id": _text(record, "specimen_id"),
        "source_ref": _text(record, "source_ref"),
        "method": _text(record, "method"),
        "status": record["status"],
    }


def _calculated_value(report: Mapping, definition: Mapping) -> float | None:
    section = (report.get("sections") or {}).get(definition["section"]) or {}
    if section.get("status") != "AVAILABLE":
        return None
    value = (section.get("values") or {}).get(definition["value_key"])
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def compare_observed_outcomes(
    calculated_report: Mapping,
    observations: Sequence[Mapping],
    *,
    experiment_id: str,
    context: Mapping[str, str],
) -> dict:
    """Link observations to compatible deterministic outputs.

    The residual is ``observed - calculated``. A result is never labelled as
    validation success; acceptance and generalisation remain unassessed.
    """
    if not isinstance(calculated_report, Mapping) or not isinstance(calculated_report.get("sections"), Mapping):
        raise ExperimentValidationError("CALCULATED_REPORT_REQUIRED")
    if not isinstance(experiment_id, str) or not experiment_id.strip() or len(experiment_id) > 160:
        raise ExperimentValidationError("INVALID_EXPERIMENT_ID")
    if not isinstance(context, Mapping) or not context or any(
        not isinstance(key, str) or not isinstance(value, str) or not value.strip()
        for key, value in context.items()
    ):
        raise ExperimentValidationError("INVALID_EXPERIMENT_CONTEXT")
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)) or not 1 <= len(observations) <= 1000:
        raise ExperimentValidationError("OBSERVATIONS_REQUIRED")

    clean_observations = [_validate_observation(item) for item in observations]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for observation in clean_observations:
        grouped[observation["observable"]].append(observation)

    comparisons = {}
    warnings = []
    unavailable = []
    for observable, definition in OBSERVABLES.items():
        rows = grouped.get(observable, [])
        calculated = _calculated_value(calculated_report, definition)
        if not rows:
            comparisons[observable] = {
                "status": "UNAVAILABLE",
                "reason": "OBSERVATION_NOT_PROVIDED",
                "evidence_kind": "OBSERVED",
                "method_kind": "EMPIRICAL",
                "calculated": calculated,
                "observed": None,
                "unit": definition["unit"],
                "observation_count": 0,
                "independent_specimen_count": 0,
            }
            unavailable.append(observable)
            continue
        if calculated is None:
            comparisons[observable] = {
                "status": "UNAVAILABLE",
                "reason": "CALCULATED_COUNTERPART_UNAVAILABLE",
                "evidence_kind": "OBSERVED",
                "method_kind": "EMPIRICAL",
                "calculated": None,
                "observed": statistics.mean(row["value"] for row in rows),
                "unit": definition["unit"],
                "observation_count": len(rows),
                "independent_specimen_count": len({row["specimen_id"] for row in rows}),
            }
            unavailable.append(observable)
            continue
        observed = statistics.mean(row["value"] for row in rows)
        comparisons[observable] = {
            "status": "AVAILABLE",
            "evidence_kind": "CALCULATED",
            "method_kind": "DETERMINISTIC_COMPARISON",
            "calculated": calculated,
            "observed": observed,
            "residual_observed_minus_calculated": observed - calculated,
            "absolute_error": abs(observed - calculated),
            "unit": definition["unit"],
            "observation_count": len(rows),
            "independent_specimen_count": len({row["specimen_id"] for row in rows}),
            "observation_statuses": sorted({row["status"] for row in rows}),
            "sample_sd": statistics.stdev(row["value"] for row in rows) if len(rows) > 1 else None,
        }
        if any(row["status"] == "REPORTED" for row in rows):
            warnings.append(f"{observable}: en az bir kayıt cihaz ölçümü değil REPORTED olarak işaretlendi.")

    status = "COMPARED" if not unavailable else "PARTIAL"
    snapshot = {
        "experiment_id": experiment_id,
        "context": deepcopy(dict(context)),
        "calculated_report": deepcopy(dict(calculated_report)),
        "observations": clean_observations,
    }
    return {
        "schema_version": "experiment-validation-v1",
        "engine_version": VERSION,
        "status": status,
        "evidence_kind": "CALCULATED",
        "method_kind": "DETERMINISTIC_COMPARISON",
        "qualifier": "OBSERVED_VS_CALCULATED_NOT_VALIDATION_APPROVAL",
        "input_hash": digest({"version": VERSION, "input": snapshot}),
        "input_snapshot": snapshot,
        "comparisons": comparisons,
        "warnings": warnings,
        "unavailable_sections": unavailable,
        "limitations": [
            "Residual gözlenen eksi hesaplanan olarak tanımlıdır; pozitif değer gözlemin daha yüksek olduğunu gösterir.",
            "Aynı specimen_id altındaki tekrarlar bağımsız deney sayılmaz.",
            "Bu rapor kabul, güvenlik, genelleme veya model doğrulaması onayı değildir.",
            "Ölçüm yöntemi, cihaz kalibrasyonu ve numune bağlamı kullanıcı tarafından izlenebilir tutulmalıdır.",
        ],
    }
