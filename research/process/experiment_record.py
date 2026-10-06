"""Immutable local records for an experiment and its specimen context.

This is a persistence bridge, not a database or a scientific predictor.  The
record keeps the identifiers and provenance needed to attach later
observations without inventing missing firing or material information.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping

from research.chemistry.foundation import digest


VERSION = "experiment-record/0.1.0"
_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ExperimentRecordError(ValueError):
    """An experiment record cannot be safely stored or loaded."""


def _canonical(value: Mapping) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ExperimentRecordError("RECORD_NOT_JSON_SERIALIZABLE") from exc


def _record_id(record: Mapping) -> str:
    if record.get("schema_version") != "experiment-record-v1":
        raise ExperimentRecordError("UNSUPPORTED_EXPERIMENT_RECORD_SCHEMA")
    value = record.get("record_id")
    if not isinstance(value, str) or not _ID_PATTERN.fullmatch(value):
        raise ExperimentRecordError("INVALID_EXPERIMENT_RECORD_ID")
    return value


def _path_for(record_id: str, root: Path) -> Path:
    if not _ID_PATTERN.fullmatch(record_id):
        raise ExperimentRecordError("INVALID_EXPERIMENT_RECORD_ID")
    return root / f"{record_id}.json"


def build_record(payload: Mapping) -> dict:
    """Build an immutable record and report explicit missing context."""
    snapshot = dict(payload)
    context = snapshot.get("context")
    if not isinstance(context, Mapping):
        raise ExperimentRecordError("EXPERIMENT_CONTEXT_REQUIRED")
    required_context = ("body_revision", "glaze_revision", "application_revision", "firing_run_id")
    missing_context = [key for key in required_context if not str(context.get(key, "")).strip()]
    record = {
        "schema_version": "experiment-record-v1",
        "engine_version": VERSION,
        "experiment_id": snapshot.get("experiment_id"),
        "specimen_id": snapshot.get("specimen_id"),
        "record_kind": snapshot.get("record_kind"),
        "question": snapshot.get("question", ""),
        "source_ref": snapshot.get("source_ref"),
        "context": {key: str(context.get(key, "")) for key in required_context},
        "analysis_report_id": snapshot.get("analysis_report_id"),
        "chemistry_input_hash": snapshot.get("chemistry_input_hash"),
        "missing_context": missing_context,
        "notes": snapshot.get("notes", ""),
    }
    record["record_id"] = digest({"version": VERSION, "record": record})
    return record


def _read(path: Path) -> dict:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentRecordError("EXPERIMENT_RECORD_READ_FAILED") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "experiment-record-archive-v1":
        raise ExperimentRecordError("INVALID_EXPERIMENT_RECORD_ARCHIVE")
    record = envelope.get("record")
    if not isinstance(record, dict) or envelope.get("record_id") != record.get("record_id"):
        raise ExperimentRecordError("EXPERIMENT_RECORD_ID_MISMATCH")
    if envelope.get("record_sha256") != digest(record):
        raise ExperimentRecordError("EXPERIMENT_RECORD_CHECKSUM_MISMATCH")
    _record_id(record)
    return envelope


def save_experiment_record(record: Mapping, archive_root: Path | str) -> dict:
    record_id = _record_id(record)
    root = Path(archive_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = _path_for(record_id, root)
    record_sha256 = digest(record)
    envelope = {
        "schema_version": "experiment-record-archive-v1",
        "record_id": record_id,
        "record_sha256": record_sha256,
        "record": dict(record),
    }
    if path.exists():
        existing = _read(path)
        if existing["record_sha256"] != record_sha256:
            raise ExperimentRecordError("EXPERIMENT_RECORD_ID_CONFLICT")
        return {"status": "EXISTS", "record_id": record_id, "record_sha256": record_sha256}
    with NamedTemporaryFile("w", encoding="utf-8", dir=root, prefix=f".{record_id}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(_canonical(envelope))
        handle.flush()
    try:
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"status": "CREATED", "record_id": record_id, "record_sha256": record_sha256, "record": dict(record)}


def load_experiment_record(record_id: str, archive_root: Path | str) -> dict:
    path = _path_for(record_id, Path(archive_root).resolve())
    if not path.is_file():
        raise FileNotFoundError(record_id)
    envelope = _read(path)
    return {
        "status": "AVAILABLE",
        "record_id": envelope["record_id"],
        "record_sha256": envelope["record_sha256"],
        "record": envelope["record"],
    }
