"""M2 local JSON intake. Standard library only; never fetches external data.

Rights decisions are operator-supplied in a separate file, not trusted from the
source payload. This checks explicit decisions, not the legal validity of them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
from datetime import date, datetime, timezone
from uuid import uuid4

POLICY_VERSION = "material-intake-v1.0"
SCHEMA_VERSION = "material-analysis-intake-v1"
OXIDES = frozenset("SiO2 Al2O3 Na2O K2O CaO MgO ZnO BaO SrO Li2O B2O3 TiO2 ZrO2 Fe2O3 CoO CuO MnO2 SnO2 P2O5".split())
PURPOSES = ("INTERNAL_VALIDATION", "INTERNAL_REFERENCE")
SOURCE_FIELDS = ("source_name", "source_url", "source_type", "source_author",
                 "source_license", "retrieval_date")


class IntakeError(ValueError):
    """A controlled intake failure, safe to print without source data."""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def load_json_bytes(raw):
    try:
        result = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                            parse_constant=lambda _: (_ for _ in ()).throw(IntakeError("NON_FINITE_JSON")))
        canonical(result)  # catches numeric overflow such as 1e999
        return result
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        if isinstance(exc, IntakeError):
            raise
        raise IntakeError("INVALID_JSON") from None


def read_json(path):
    return load_json_bytes(Path(path).read_bytes())


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def _date(value):
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def preflight(envelope, ledger, purpose):
    """Before raw storage, require explicit permission for every source present."""
    if purpose not in PURPOSES:
        raise IntakeError("UNSUPPORTED_PURPOSE")
    if not isinstance(envelope, dict) or envelope.get("schema_version") != SCHEMA_VERSION:
        raise IntakeError("UNSUPPORTED_SCHEMA")
    sources, records = envelope.get("sources"), envelope.get("records")
    if not isinstance(sources, dict) or not sources or not isinstance(records, list):
        raise IntakeError("INVALID_ENVELOPE")
    if not isinstance(ledger, dict) or ledger.get("schema_version") != "rights-decisions-v1":
        raise IntakeError("INVALID_RIGHTS_LEDGER")
    decisions = ledger.get("sources")
    if not isinstance(decisions, dict):
        raise IntakeError("INVALID_RIGHTS_LEDGER")
    for source_id, source in sources.items():
        decision = decisions.get(source_id)
        if not isinstance(source, dict) or not isinstance(decision, dict):
            raise IntakeError("SOURCE_RIGHTS_NOT_REVIEWED")
        if decision.get("store") != "ALLOWED":
            raise IntakeError("RAW_STORAGE_NOT_ALLOWED")
        if not all(_text(decision.get(k)) for k in ("reviewer", "evidence", "decision_version")) or not _date(decision.get("checked_at")):
            raise IntakeError("RIGHTS_EVIDENCE_MISSING")
        for field in ("purposes", "approved_analysis_hashes"):
            values = decision.get(field, [])
            if not isinstance(values, list) or not all(_text(v) for v in values):
                raise IntakeError("INVALID_RIGHTS_LEDGER")
    for record in records:
        if not isinstance(record, dict) or not _text(record.get("source_id")) or record["source_id"] not in sources:
            raise IntakeError("UNRESOLVED_RECORD_SOURCE")
    return sources, records, decisions


def validate_record(record, source, decision, purpose):
    """Preserve quantities; never close analyses to 100 or infer missing oxides."""
    issues = []

    def issue(code, path, hard=False):
        issues.append({"code": code, "path": path,
                       "severity": "ERROR" if hard else "REVIEW_REQUIRED"})

    for field in ("record_id", "analysis_version", "material_id", "material_name"):
        if not _text(record.get(field)):
            issue("MISSING_IDENTITY", field)
    for field in SOURCE_FIELDS:
        if not _text(source.get(field)):
            issue("SOURCE_METADATA_MISSING", "source." + field)
    if not _date(source.get("retrieval_date")):
        issue("INVALID_RETRIEVAL_DATE", "source.retrieval_date")
    for field in ("attribution_required", "share_alike_required"):
        if source.get(field) not in ("REQUIRED", "NOT_REQUIRED", "UNKNOWN"):
            issue("SOURCE_METADATA_MISSING", "source." + field)
    if source.get("commercial_use_allowed") not in ("ALLOWED", "DENIED", "UNKNOWN"):
        issue("SOURCE_METADATA_MISSING", "source.commercial_use_allowed")
    if decision.get("derive") != "ALLOWED" or purpose not in decision.get("purposes", []):
        issue("PURPOSE_NOT_ALLOWED", "rights")
    kind = record.get("record_kind")
    if kind not in ("SYNTHETIC_TEST_ONLY", "REPORTED"):
        issue("UNKNOWN_RECORD_KIND", "record_kind")
    if kind == "SYNTHETIC_TEST_ONLY" and purpose != "INTERNAL_VALIDATION":
        issue("SYNTHETIC_NOT_REFERENCE_DATA", "record_kind")
    if kind == "REPORTED":
        reviews = decision.get("approved_analysis_hashes", [])
        if digest(record) not in reviews:
            issue("RECORD_REVIEW_REQUIRED", "record")
    if not _date(record.get("analysis_date")):
        issue("ANALYSIS_DATE_UNKNOWN", "analysis_date")
    if not _text(record.get("method")):
        issue("ANALYSIS_METHOD_UNKNOWN", "method")
    basis = record.get("analysis_basis")
    if basis not in ("DRY", "AS_RECEIVED", "IGNITED"):
        issue("ANALYSIS_BASIS_UNKNOWN", "analysis_basis")
    if record.get("coverage") != "COMPLETE_REPORTED":
        issue("INCOMPLETE_CHEMISTRY", "coverage")
    if not _text(record.get("omitted_oxides_statement")):
        issue("OMITTED_OXIDES_UNDEFINED", "omitted_oxides_statement")
    oxides = record.get("oxides")
    total = None
    if not isinstance(oxides, dict) or not oxides:
        issue("MISSING_CHEMISTRY", "oxides")
    else:
        values = []
        for formula, value in oxides.items():
            path = "oxides." + formula
            if formula not in OXIDES:
                issue("UNSUPPORTED_OXIDE", path)
            if not _number(value):
                issue("UNSUPPORTED_VALUE_FORMAT", path)
            elif value < 0 or value > 100:
                issue("INVALID_OXIDE_PERCENTAGE", path, hard=True)
            else:
                values.append(value)
        if len(values) == len(oxides):
            total = math.fsum(values)
    loi, moisture = record.get("loi_pct"), record.get("moisture_pct")
    for key, value in (("loi_pct", loi), ("moisture_pct", moisture)):
        if value is not None and not _number(value):
            issue("UNSUPPORTED_VALUE_FORMAT", key)
        elif value is not None and (value > 100 or (key == "moisture_pct" and value < 0)):
            issue("INVALID_PERCENTAGE", key, hard=True)
    if _number(loi) and loi < 0:
        issue("UNSUPPORTED_MASS_CHANGE_MODEL", "loi_pct")
    if basis == "DRY" and (not _number(loi) or record.get("loi_reference_basis") != "DRY"):
        issue("LOI_BASIS_UNRESOLVED", "loi_reference_basis")
    if basis == "AS_RECEIVED" and (not _number(loi) or record.get("loi_reference_basis") != "AS_RECEIVED" or record.get("loi_includes_moisture") is not True):
        issue("LOI_BASIS_UNRESOLVED", "loi_reference_basis")
    if basis == "IGNITED" and (not _number(loi) or record.get("loi_reference_basis") not in ("DRY", "AS_RECEIVED")):
        issue("LOI_BASIS_UNRESOLVED", "loi_reference_basis")
    if moisture is not None and record.get("moisture_reference_basis") != "AS_RECEIVED":
        issue("MOISTURE_BASIS_UNRESOLVED", "moisture_reference_basis")
    if record.get("loi_reference_basis") == "AS_RECEIVED" and record.get("loi_includes_moisture") is not True:
        issue("LOI_BASIS_UNRESOLVED", "loi_includes_moisture")
    if _number(loi) and _number(moisture) and record.get("loi_reference_basis") == "AS_RECEIVED" and loi < moisture:
        issue("INCONSISTENT_BASIS_METADATA", "loi_pct")
    balanced_total = None
    if total is not None and basis in ("DRY", "AS_RECEIVED", "IGNITED"):
        if basis == "IGNITED":
            balanced_total = total
        elif _number(loi):
            balanced_total = total + loi  # total AR LOI already includes moisture
        if balanced_total is not None and abs(balanced_total - 100) > 0.5:
            issue("ANALYSIS_TOTAL_REVIEW", "oxides")
    if any(i["severity"] == "ERROR" for i in issues):
        status = "rejected"
    else:
        status = "quarantined" if issues else "accepted"
    normalized = None
    if status == "accepted":
        normalized = {
            "record_kind": kind, "analysis": record,
            "source_metadata": source, "rights_decision": decision,
            "reported_oxide_total": total, "basis_balance_total": balanced_total,
            "missing_values_policy": "NEVER_INFER_ZERO",
            "quality": {"basis_known": True, "coverage": record["coverage"],
                        "source_type": source["source_type"],
                        "physical_validation": "NOT_APPLICABLE" if kind == "SYNTHETIC_TEST_ONLY" else "NOT_VERIFIED",
                        "uncertainty_known": False},
        }
    return status, issues, normalized


def analyze(envelope, ledger, purpose, seen=()):
    sources, records, decisions = preflight(envelope, ledger, purpose)
    seen = set(seen)
    counts = {key: 0 for key in ("received", "accepted", "quarantined", "rejected", "duplicate_skipped",
                                "duplicates", "unknown_materials", "missing_chemistry", "license_conflicts")}
    normalized, dispositions = [], []
    for row, record in enumerate(records):
        source_id = record["source_id"]
        content_hash = digest(record)
        record_key = digest({"source_id": source_id, "record_id": record.get("record_id"), "content_hash": content_hash})
        decision_key = digest({"record_key": record_key, "source": sources[source_id],
                               "rights": decisions[source_id], "policy": POLICY_VERSION, "purpose": purpose})
        status, issues, output = validate_record(record, sources[source_id], decisions[source_id], purpose)
        duplicate = decision_key in seen
        seen.add(decision_key)
        counts["received"] += 1
        codes = {i["code"] for i in issues}
        if "MISSING_IDENTITY" in codes:
            counts["unknown_materials"] += 1
        if codes & {"MISSING_CHEMISTRY", "INCOMPLETE_CHEMISTRY", "UNSUPPORTED_VALUE_FORMAT"}:
            counts["missing_chemistry"] += 1
        if "PURPOSE_NOT_ALLOWED" in codes:
            counts["license_conflicts"] += 1
        if duplicate:
            status = "duplicate_skipped"
            counts["duplicates"] += 1
        counts[status] += 1
        dispositions.append({"row": row, "source_id": source_id, "source_record_id": record.get("record_id"),
                             "record_key": record_key, "content_hash": content_hash,
                             "decision_key": decision_key, "status": status, "issues": issues})
        if status == "accepted":
            output.update(record_key=record_key, decision_key=decision_key, content_hash=content_hash)
            normalized.append(output)
    assert counts["received"] == sum(counts[k] for k in ("accepted", "quarantined", "rejected", "duplicate_skipped"))
    return {"policy_version": POLICY_VERSION, "purpose": purpose, "counts": counts,
            "dispositions": dispositions, "normalized": normalized}


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _seen_decisions(root):
    seen = set()
    for directory in sorted((root / "runs").glob("*")):
        manifest = read_json(directory / "processed" / "manifest.json")
        for relative, expected in manifest["artifacts"].items():
            target = (directory / relative).resolve()
            if not target.is_relative_to(directory.resolve()):
                raise IntakeError("UNSAFE_MANIFEST_PATH")
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                raise IntakeError("STORED_ARTIFACT_CHECKSUM_MISMATCH")
        seen.update(manifest["decision_keys"])
    return seen


def import_file(input_path, ledger_path, storage_dir, purpose):
    raw = Path(input_path).read_bytes()
    envelope, ledger = load_json_bytes(raw), read_json(ledger_path)
    preflight(envelope, ledger, purpose)  # no raw persisted before rights check
    root = Path(storage_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    lock = root / ".import.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise IntakeError("IMPORT_LOCKED_REVIEW_STALE_LOCK_BEFORE_REMOVAL") from None
    os.close(fd)
    staging = None
    try:
        result = analyze(envelope, ledger, purpose, _seen_decisions(root))
        run_id = uuid4().hex
        (root / "runs").mkdir(exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".pending-", dir=root))
        (staging / "raw").mkdir()
        (staging / "raw" / "source.json").write_bytes(raw)
        _write_json(staging / "raw" / "rights-decisions.json", ledger)
        _write_json(staging / "staging" / "dispositions.json", result["dispositions"])
        _write_json(staging / "normalized" / "records.json", result["normalized"])
        report = {"run_id": run_id, "state": "COMMITTED", "policy_version": POLICY_VERSION,
                  "purpose": purpose, "counts": result["counts"],
                  "scope": "LOCAL_INTERNAL_ONLY", "created_at": datetime.now(timezone.utc).isoformat()}
        _write_json(staging / "processed" / "report.json", report)
        artifacts = {p.relative_to(staging).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(staging.rglob("*.json"))}
        manifest = {"schema_version": "intake-manifest-v1", "run_id": run_id,
                    "policy_version": POLICY_VERSION, "purpose": purpose,
                    "raw_sha256": hashlib.sha256(raw).hexdigest(), "rights_sha256": digest(ledger),
                    "artifacts": artifacts,
                    "decision_keys": [d["decision_key"] for d in result["dispositions"]],
                    "accepted_members": [{"record_key": r["record_key"], "decision_key": r["decision_key"],
                                          "content_hash": r["content_hash"]} for r in result["normalized"]],
                    "release_status": "INTERNAL_VALIDATION_ONLY" if purpose == "INTERNAL_VALIDATION" else "INTERNAL_REFERENCE_ONLY"}
        _write_json(staging / "processed" / "manifest.json", manifest)
        os.replace(staging, root / "runs" / run_id)  # publish complete bundle on same filesystem
        staging = None
        return report
    finally:
        if staging is not None:
            # Only our freshly created, exact temporary directory is cleaned up.
            resolved = staging.resolve()
            if resolved.parent != root or not resolved.name.startswith(".pending-"):
                raise IntakeError("UNSAFE_CLEANUP_PATH")
            shutil.rmtree(resolved)
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "import"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--rights", type=Path, required=True)
    parser.add_argument("--purpose", choices=PURPOSES, required=True)
    parser.add_argument("--storage", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "import":
            if args.storage is None:
                parser.error("import requires --storage")
            result = import_file(args.input, args.rights, args.storage, args.purpose)
        else:
            result = analyze(read_json(args.input), read_json(args.rights), args.purpose)
            result = {k: v for k, v in result.items() if k != "normalized"}
        print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
        counts = result["counts"]
        return 2 if counts["quarantined"] or counts["rejected"] else 0
    except (IntakeError, OSError, KeyError, TypeError) as exc:
        code = str(exc) if isinstance(exc, IntakeError) else "IO_OR_STORAGE_FORMAT_ERROR"
        print(json.dumps({"state": "FAILED", "code": code}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
