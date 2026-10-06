"""Local immutable archive for observed-outcome validation runs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping

from research.chemistry.foundation import digest


DEFAULT_ARCHIVE_ROOT = Path(__file__).resolve().parents[2] / "storage" / "experiment-runs"
_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ExperimentArchiveError(ValueError):
    """A validation run cannot be safely stored or loaded."""


def _path_for(run_id: str, archive_root: Path) -> Path:
    if not isinstance(run_id, str) or not _ID_PATTERN.fullmatch(run_id):
        raise ExperimentArchiveError("INVALID_EXPERIMENT_RUN_ID")
    return archive_root / f"{run_id}.json"


def _canonical(value: Mapping) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ExperimentArchiveError("RUN_NOT_JSON_SERIALIZABLE") from exc


def _run_id(report: Mapping) -> str:
    if report.get("schema_version") != "experiment-validation-v1":
        raise ExperimentArchiveError("UNSUPPORTED_EXPERIMENT_SCHEMA")
    run_id = report.get("input_hash")
    if not isinstance(run_id, str) or not _ID_PATTERN.fullmatch(run_id):
        raise ExperimentArchiveError("INVALID_EXPERIMENT_RUN_ID")
    return run_id


def _read(path: Path) -> dict:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentArchiveError("EXPERIMENT_ARCHIVE_READ_FAILED") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "experiment-archive-v1":
        raise ExperimentArchiveError("INVALID_EXPERIMENT_ARCHIVE")
    report = envelope.get("report")
    if not isinstance(report, dict) or envelope.get("run_id") != report.get("input_hash"):
        raise ExperimentArchiveError("EXPERIMENT_ARCHIVE_ID_MISMATCH")
    if envelope.get("report_sha256") != digest(report):
        raise ExperimentArchiveError("EXPERIMENT_ARCHIVE_CHECKSUM_MISMATCH")
    return envelope


def save_experiment_validation(report: Mapping, archive_root: Path | str = DEFAULT_ARCHIVE_ROOT) -> dict:
    """Save one validation report atomically and reject same-id changes."""
    run_id = _run_id(report)
    report_sha256 = digest(report)
    root = Path(archive_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = _path_for(run_id, root)
    envelope = {
        "schema_version": "experiment-archive-v1",
        "run_id": run_id,
        "report_sha256": report_sha256,
        "report": report,
    }
    raw = _canonical(envelope)
    if path.exists():
        existing = _read(path)
        if existing["report_sha256"] != report_sha256:
            raise ExperimentArchiveError("EXPERIMENT_RUN_ID_CONFLICT")
        return {"status": "EXISTS", "run_id": run_id, "report_sha256": report_sha256}
    with NamedTemporaryFile("w", encoding="utf-8", dir=root, prefix=f".{run_id}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(raw)
        handle.flush()
    try:
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"status": "CREATED", "run_id": run_id, "report_sha256": report_sha256}


def load_experiment_validation(run_id: str, archive_root: Path | str = DEFAULT_ARCHIVE_ROOT) -> dict:
    """Load one validation report after checksum verification."""
    path = _path_for(run_id, Path(archive_root).resolve())
    if not path.is_file():
        raise FileNotFoundError(run_id)
    envelope = _read(path)
    return {
        "status": "AVAILABLE",
        "run_id": envelope["run_id"],
        "report_sha256": envelope["report_sha256"],
        "report": envelope["report"],
    }
