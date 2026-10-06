"""Local immutable archive for comparison-run snapshots.

This is an M5 bridge, not a database replacement. The archive keeps the
snapshot payload and a content digest together so a later PostgreSQL adapter
can preserve the same contract without changing the chemistry engine.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Mapping

from research.chemistry.foundation import digest
from research.external.comparison import replay_comparison_snapshot


DEFAULT_ARCHIVE_ROOT = Path(__file__).resolve().parents[2] / "storage" / "comparison-runs"
_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ComparisonArchiveError(ValueError):
    """A snapshot cannot be safely stored or read from the local archive."""


def _canonical_json(value: Mapping) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ComparisonArchiveError("SNAPSHOT_NOT_JSON_SERIALIZABLE") from exc


def _snapshot_id(snapshot: Mapping) -> str:
    if snapshot.get("schema_version") != "comparison-run-v1":
        raise ComparisonArchiveError("UNSUPPORTED_COMPARISON_SCHEMA")
    comparison_id = snapshot.get("input_hash")
    if not isinstance(comparison_id, str) or not _ID_PATTERN.fullmatch(comparison_id):
        raise ComparisonArchiveError("INVALID_COMPARISON_ID")
    return comparison_id


def _path_for(comparison_id: str, archive_root: Path) -> Path:
    if not isinstance(comparison_id, str) or not _ID_PATTERN.fullmatch(comparison_id):
        raise ComparisonArchiveError("INVALID_COMPARISON_ID")
    return archive_root / f"{comparison_id}.json"


def save_comparison_snapshot(snapshot: Mapping, archive_root: Path | str = DEFAULT_ARCHIVE_ROOT) -> dict:
    """Save a comparison snapshot atomically and idempotently.

    Existing identical content is returned as-is. A different payload with
    the same comparison id is rejected instead of being overwritten.
    """
    comparison_id = _snapshot_id(snapshot)
    snapshot_sha256 = digest(snapshot)
    root = Path(archive_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = _path_for(comparison_id, root)
    envelope = {
        "schema_version": "comparison-archive-v1",
        "comparison_id": comparison_id,
        "snapshot_sha256": snapshot_sha256,
        "snapshot": snapshot,
    }
    raw_envelope = _canonical_json(envelope)
    if path.exists():
        existing = _read_envelope(path)
        if existing["snapshot_sha256"] != snapshot_sha256:
            raise ComparisonArchiveError("COMPARISON_ID_CONFLICT")
        return {
            "status": "EXISTS",
            "comparison_id": comparison_id,
            "snapshot_sha256": snapshot_sha256,
            "replay": replay_comparison_snapshot(existing["snapshot"]),
        }
    with NamedTemporaryFile("w", encoding="utf-8", dir=root, prefix=f".{comparison_id}.", suffix=".tmp", delete=False) as handle:
        temporary_path = Path(handle.name)
        handle.write(raw_envelope)
        handle.flush()
    try:
        temporary_path.replace(path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
    return {
        "status": "CREATED",
        "comparison_id": comparison_id,
        "snapshot_sha256": snapshot_sha256,
        "replay": replay_comparison_snapshot(snapshot),
    }


def _read_envelope(path: Path) -> dict:
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComparisonArchiveError("ARCHIVE_READ_FAILED") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "comparison-archive-v1":
        raise ComparisonArchiveError("INVALID_ARCHIVE_ENVELOPE")
    snapshot = envelope.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ComparisonArchiveError("INVALID_ARCHIVE_SNAPSHOT")
    if envelope.get("comparison_id") != snapshot.get("input_hash"):
        raise ComparisonArchiveError("ARCHIVE_ID_MISMATCH")
    if envelope.get("snapshot_sha256") != digest(snapshot):
        raise ComparisonArchiveError("ARCHIVE_CHECKSUM_MISMATCH")
    return envelope


def load_comparison_snapshot(comparison_id: str, archive_root: Path | str = DEFAULT_ARCHIVE_ROOT) -> dict:
    """Load and checksum-verify one archived comparison run."""
    path = _path_for(comparison_id, Path(archive_root).resolve())
    if not path.is_file():
        raise FileNotFoundError(comparison_id)
    envelope = _read_envelope(path)
    replay = replay_comparison_snapshot(envelope["snapshot"])
    return {
        "status": "AVAILABLE",
        "comparison_id": envelope["comparison_id"],
        "snapshot_sha256": envelope["snapshot_sha256"],
        "snapshot": envelope["snapshot"],
        "replay": replay,
    }
