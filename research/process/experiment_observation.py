"""Immutable specimen observations linked to an ExperimentRecord."""

from __future__ import annotations

import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping

from research.chemistry.foundation import digest
from research.process.experiment_validation import ExperimentValidationError, _validate_observation


VERSION = "experiment-observation/0.1.0"
_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ExperimentObservationError(ValueError):
    """An observation cannot be safely stored or loaded."""


def build_observation(record_id: str, payload: Mapping) -> dict:
    if not isinstance(record_id, str) or not _ID_PATTERN.fullmatch(record_id):
        raise ExperimentObservationError("INVALID_EXPERIMENT_RECORD_ID")
    try:
        observation = _validate_observation(payload)
    except ExperimentValidationError as exc:
        raise ExperimentObservationError(str(exc)) from exc
    snapshot = {"record_id": record_id, "observation": observation}
    return {
        "schema_version": "experiment-observation-v1",
        "engine_version": VERSION,
        "record_id": record_id,
        "observation_id": digest({"version": VERSION, "snapshot": snapshot}),
        "observation": observation,
    }


def _path_for(observation_id: str, root: Path) -> Path:
    if not isinstance(observation_id, str) or not _ID_PATTERN.fullmatch(observation_id):
        raise ExperimentObservationError("INVALID_EXPERIMENT_OBSERVATION_ID")
    return root / f"{observation_id}.json"


def _canonical(value: Mapping) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ExperimentObservationError("OBSERVATION_NOT_JSON_SERIALIZABLE") from exc


def _read(path: Path) -> dict:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExperimentObservationError("EXPERIMENT_OBSERVATION_READ_FAILED") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "experiment-observation-archive-v1":
        raise ExperimentObservationError("INVALID_EXPERIMENT_OBSERVATION_ARCHIVE")
    observation = envelope.get("observation")
    if not isinstance(observation, dict) or envelope.get("observation_id") != observation.get("observation_id"):
        raise ExperimentObservationError("EXPERIMENT_OBSERVATION_ID_MISMATCH")
    if envelope.get("observation_sha256") != digest(observation):
        raise ExperimentObservationError("EXPERIMENT_OBSERVATION_CHECKSUM_MISMATCH")
    return envelope


def save_observation(observation: Mapping, archive_root: Path | str) -> dict:
    observation_id = observation.get("observation_id")
    if not isinstance(observation_id, str) or not _ID_PATTERN.fullmatch(observation_id):
        raise ExperimentObservationError("INVALID_EXPERIMENT_OBSERVATION_ID")
    record_id = observation.get("record_id")
    if not isinstance(record_id, str) or not _ID_PATTERN.fullmatch(record_id):
        raise ExperimentObservationError("INVALID_EXPERIMENT_RECORD_ID")
    root = Path(archive_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = _path_for(observation_id, root)
    observation_sha256 = digest(observation)
    envelope = {
        "schema_version": "experiment-observation-archive-v1",
        "observation_id": observation_id,
        "observation_sha256": observation_sha256,
        "observation": dict(observation),
    }
    if path.exists():
        existing = _read(path)
        if existing["observation_sha256"] != observation_sha256:
            raise ExperimentObservationError("EXPERIMENT_OBSERVATION_ID_CONFLICT")
        return {"status": "EXISTS", "observation_id": observation_id, "observation_sha256": observation_sha256, "observation": dict(observation)}
    with NamedTemporaryFile("w", encoding="utf-8", dir=root, prefix=f".{observation_id}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(_canonical(envelope))
        handle.flush()
    try:
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"status": "CREATED", "observation_id": observation_id, "observation_sha256": observation_sha256, "observation": dict(observation)}


def load_observation(observation_id: str, archive_root: Path | str) -> dict:
    path = _path_for(observation_id, Path(archive_root).resolve())
    if not path.is_file():
        raise FileNotFoundError(observation_id)
    envelope = _read(path)
    return {
        "status": "AVAILABLE",
        "observation_id": envelope["observation_id"],
        "observation_sha256": envelope["observation_sha256"],
        "observation": envelope["observation"],
    }


def list_observations(record_id: str, archive_root: Path | str) -> list[dict]:
    if not isinstance(record_id, str) or not _ID_PATTERN.fullmatch(record_id):
        raise ExperimentObservationError("INVALID_EXPERIMENT_RECORD_ID")
    root = Path(archive_root).resolve()
    if not root.is_dir():
        return []
    results = []
    for path in sorted(root.glob("*.json")):
        envelope = _read(path)
        if envelope["observation"].get("record_id") == record_id:
            results.append({
                "status": "AVAILABLE",
                "observation_id": envelope["observation_id"],
                "observation_sha256": envelope["observation_sha256"],
                "observation": envelope["observation"],
            })
    return results
