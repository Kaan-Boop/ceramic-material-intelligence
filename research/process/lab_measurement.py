"""Typed, provenance-rich empirical records for fired ceramic specimens.

These records are observations only. They do not create model predictions or
make measurements comparable with a calculated quantity unless a separate,
explicit validation method defines that counterpart.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping


VERSION = "lab-measurement/0.1.0"
_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_NUMERIC = {
    "drying_linear_shrinkage_pct": {"unit": "%", "low": -100.0, "high": 100.0},
    "firing_linear_shrinkage_pct": {"unit": "%", "low": -100.0, "high": 100.0},
    "glaze_runout_distance_mm": {"unit": "mm", "low": 0.0, "high": 100000.0},
    "water_absorption_mass_pct": {"unit": "%", "low": 0.0, "high": 1000.0},
    "gloss_mean_gu": {"unit": "GU", "low": 0.0, "high": 2000.0},
}
_CATEGORIES = {
    "glaze_surface_class": {
        "GLOSSY", "SEMI_GLOSS", "SATIN", "MATTE", "DRY_MATTE", "CRYSTALLINE",
        "TEXTURED", "CRAWLED", "METALLIC", "LUSTER", "OTHER",
    },
    "optical_transmission_class": {"TRANSPARENT", "TRANSLUCENT", "OPAQUE", "OTHER"},
    "glaze_adhesion_assessment": {"ADHERED", "PARTIAL_PEELING", "PEELED", "OTHER"},
}
_DEFECTS = {
    "CRAZING", "SHIVERING", "CRAWLING", "PINHOLING", "BLISTERING", "BLOATING",
    "DUNTING", "CRATERING", "RUNNING", "CLOUDING", "DEVITRIFICATION", "SETTLING",
    "WARPING", "BLACK_CORE", "CRACKING", "PEELING", "OTHER",
}


class LabMeasurementError(ValueError):
    """An empirical record is invalid or cannot be safely archived."""


def _canonical(value: Mapping) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise LabMeasurementError("MEASUREMENT_NOT_JSON_SERIALIZABLE") from exc


def _digest(value: Mapping) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(record: Mapping, key: str, *, maximum: int = 500) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > maximum:
        raise LabMeasurementError(f"INVALID_OR_MISSING:{key.upper()}")
    return value.strip()


def _safe_conditions(value: object) -> dict:
    if not isinstance(value, Mapping):
        raise LabMeasurementError("INVALID_CONDITIONS")
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise LabMeasurementError("INVALID_CONDITIONS") from exc
    if len(encoded.encode("utf-8")) > 16_384:
        raise LabMeasurementError("CONDITIONS_TOO_LARGE")
    return json.loads(encoded)


def _number(value: object, *, low: float, high: float, key: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise LabMeasurementError(f"INVALID_NUMBER:{key.upper()}")
    if not low <= value <= high:
        raise LabMeasurementError(f"OUT_OF_RANGE:{key.upper()}")
    return float(value)


def build_measurement(record_id: str, payload: Mapping) -> dict:
    """Validate and freeze one quantitative, categorical, or defect observation."""
    if not isinstance(record_id, str) or not _ID_PATTERN.fullmatch(record_id):
        raise LabMeasurementError("INVALID_EXPERIMENT_RECORD_ID")
    if not isinstance(payload, Mapping):
        raise LabMeasurementError("INVALID_MEASUREMENT")

    allowed = {
        "observable", "value", "unit", "specimen_id", "source_ref", "method", "status",
        "uncertainty", "uncertainty_kind", "replicate_id", "conditions",
    }
    if set(payload) - allowed:
        raise LabMeasurementError("UNKNOWN_MEASUREMENT_FIELDS")

    observable = payload.get("observable")
    value = payload.get("value")
    unit = payload.get("unit")
    status = payload.get("status")
    uncertainty = payload.get("uncertainty")
    uncertainty_kind = payload.get("uncertainty_kind")

    if not isinstance(observable, str):
        raise LabMeasurementError("UNSUPPORTED_OBSERVABLE")
    if not isinstance(status, str):
        raise LabMeasurementError("INVALID_MEASUREMENT_STATUS")

    if observable in _NUMERIC:
        definition = _NUMERIC[observable]
        if unit != definition["unit"]:
            raise LabMeasurementError("UNIT_MISMATCH")
        if status not in {"MEASURED", "REPORTED"}:
            raise LabMeasurementError("INVALID_QUANTITATIVE_STATUS")
        clean_value = _number(value, low=definition["low"], high=definition["high"], key="value")
        clean_uncertainty = None if uncertainty is None else _number(
            uncertainty, low=0.0, high=definition["high"] - definition["low"], key="uncertainty"
        )
        allowed_uncertainty_kinds = {
            "STANDARD_UNCERTAINTY", "EXPANDED_UNCERTAINTY", "REPEAT_SD",
            "INSTRUMENT_RESOLUTION", "REPORTED_UNSPECIFIED",
        }
        if (clean_uncertainty is None) != (uncertainty_kind is None):
            raise LabMeasurementError("UNCERTAINTY_VALUE_AND_KIND_MUST_MATCH")
        if uncertainty_kind is not None and (
            not isinstance(uncertainty_kind, str) or uncertainty_kind not in allowed_uncertainty_kinds
        ):
            raise LabMeasurementError("INVALID_UNCERTAINTY_KIND")
        clean_unit = definition["unit"]
    elif observable in _CATEGORIES:
        if unit is not None or not isinstance(value, str) or value not in _CATEGORIES[observable]:
            raise LabMeasurementError("INVALID_CATEGORICAL_VALUE")
        if status not in {"OBSERVED", "REPORTED"}:
            raise LabMeasurementError("INVALID_CATEGORICAL_STATUS")
        if uncertainty is not None or uncertainty_kind is not None:
            raise LabMeasurementError("UNCERTAINTY_NOT_APPLICABLE")
        clean_value = value
        clean_uncertainty = None
        uncertainty_kind = None
        clean_unit = None
    elif observable == "defect_observation":
        if unit is not None or not isinstance(value, str) or value not in _DEFECTS:
            raise LabMeasurementError("INVALID_DEFECT_CATEGORY")
        if status not in {"OBSERVED_PRESENT", "OBSERVED_ABSENT", "NOT_ASSESSED", "REPORTED_PRESENT", "REPORTED_ABSENT"}:
            raise LabMeasurementError("INVALID_DEFECT_STATUS")
        if uncertainty is not None or uncertainty_kind is not None:
            raise LabMeasurementError("UNCERTAINTY_NOT_APPLICABLE")
        clean_value = value
        clean_uncertainty = None
        uncertainty_kind = None
        clean_unit = None
    else:
        raise LabMeasurementError("UNSUPPORTED_OBSERVABLE")

    clean = {
        "observable": observable,
        "value": clean_value,
        "unit": clean_unit,
        "specimen_id": _text(payload, "specimen_id", maximum=200),
        "source_ref": _text(payload, "source_ref"),
        "method": _text(payload, "method"),
        "status": status,
        "uncertainty": clean_uncertainty,
        "uncertainty_kind": uncertainty_kind,
        "replicate_id": None if payload.get("replicate_id") is None else _text(payload, "replicate_id", maximum=120),
        "conditions": _safe_conditions(payload.get("conditions", {})),
    }
    snapshot = {"record_id": record_id, "measurement": clean}
    return {
        "schema_version": "lab-measurement-v1",
        "engine_version": VERSION,
        "evidence_kind": "OBSERVED",
        "method_kind": "EMPIRICAL",
        "record_id": record_id,
        "measurement_id": _digest({"version": VERSION, "snapshot": snapshot}),
        "measurement": clean,
    }


def _path_for(measurement_id: str, root: Path) -> Path:
    if not isinstance(measurement_id, str) or not _ID_PATTERN.fullmatch(measurement_id):
        raise LabMeasurementError("INVALID_MEASUREMENT_ID")
    return root / f"{measurement_id}.json"


def _validate_snapshot(measurement: Mapping) -> None:
    if not isinstance(measurement, Mapping):
        raise LabMeasurementError("INVALID_MEASUREMENT_SNAPSHOT")
    rebuilt = build_measurement(measurement.get("record_id"), measurement.get("measurement"))
    if _canonical(measurement) != _canonical(rebuilt):
        raise LabMeasurementError("MEASUREMENT_SNAPSHOT_MISMATCH")


def _read(path: Path) -> dict:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LabMeasurementError("MEASUREMENT_ARCHIVE_READ_FAILED") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "lab-measurement-archive-v1":
        raise LabMeasurementError("INVALID_MEASUREMENT_ARCHIVE")
    measurement = envelope.get("measurement")
    if not isinstance(measurement, dict) or envelope.get("measurement_id") != measurement.get("measurement_id"):
        raise LabMeasurementError("MEASUREMENT_ID_MISMATCH")
    if envelope.get("measurement_sha256") != _digest(measurement):
        raise LabMeasurementError("MEASUREMENT_CHECKSUM_MISMATCH")
    _validate_snapshot(measurement)
    if path.stem != measurement["measurement_id"]:
        raise LabMeasurementError("MEASUREMENT_FILENAME_MISMATCH")
    return envelope


def save_measurement(measurement: Mapping, archive_root: Path | str) -> dict:
    _validate_snapshot(measurement)
    measurement_id = measurement.get("measurement_id")
    if not isinstance(measurement_id, str) or not _ID_PATTERN.fullmatch(measurement_id):
        raise LabMeasurementError("INVALID_MEASUREMENT_ID")
    record_id = measurement.get("record_id")
    if not isinstance(record_id, str) or not _ID_PATTERN.fullmatch(record_id):
        raise LabMeasurementError("INVALID_EXPERIMENT_RECORD_ID")
    root = Path(archive_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = _path_for(measurement_id, root)
    measurement_sha256 = _digest(measurement)
    envelope = {
        "schema_version": "lab-measurement-archive-v1",
        "measurement_id": measurement_id,
        "measurement_sha256": measurement_sha256,
        "measurement": dict(measurement),
    }
    if path.exists():
        existing = _read(path)
        if existing["measurement_sha256"] != measurement_sha256:
            raise LabMeasurementError("MEASUREMENT_ID_CONFLICT")
        return {"status": "EXISTS", "measurement_id": measurement_id, "measurement_sha256": measurement_sha256, "measurement": dict(measurement)}
    with NamedTemporaryFile("w", encoding="utf-8", dir=root, prefix=f".{measurement_id}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(_canonical(envelope))
        handle.flush()
    try:
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {
        "status": "CREATED", "measurement_id": measurement_id,
        "measurement_sha256": measurement_sha256, "measurement": dict(measurement),
    }


def load_measurement(measurement_id: str, archive_root: Path | str) -> dict:
    path = _path_for(measurement_id, Path(archive_root).resolve())
    if not path.is_file():
        raise FileNotFoundError(measurement_id)
    envelope = _read(path)
    return {
        "status": "AVAILABLE", "measurement_id": envelope["measurement_id"],
        "measurement_sha256": envelope["measurement_sha256"], "measurement": envelope["measurement"],
    }


def list_measurements(record_id: str, archive_root: Path | str) -> list[dict]:
    if not isinstance(record_id, str) or not _ID_PATTERN.fullmatch(record_id):
        raise LabMeasurementError("INVALID_EXPERIMENT_RECORD_ID")
    root = Path(archive_root).resolve()
    if not root.is_dir():
        return []
    results = []
    for path in sorted(root.glob("*.json")):
        envelope = _read(path)
        if envelope["measurement"].get("record_id") == record_id:
            results.append({
                "status": "AVAILABLE",
                "measurement_id": envelope["measurement_id"],
                "measurement_sha256": envelope["measurement_sha256"],
                "measurement": envelope["measurement"],
            })
    return results
