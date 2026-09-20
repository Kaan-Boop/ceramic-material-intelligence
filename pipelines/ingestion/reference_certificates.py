"""Validate a reviewed, partial elemental transcription; never an oxide import.

This checks structure and archived provenance, not the truth of manual transcription.
Only the four reviewed certificate hashes below are supported in this release.
"""
import argparse
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "reference-certificates-v1"
REVIEWED = {
    "SRM 70b": ("70b", "0773ca9ba9f22d41b1be1abd0fdc62a4d54444a169654ac738057d7863ba1dbe", 7),
    "SRM 97b": ("97b", "1fbc602c023b51bbcb9f6cfa7c55f8d5d98f2997d75e61e3fa2b35d59ce2b3cf", 12),
    "SRM 98b": ("98b", "bcee3992dfe56c0b6f0f8be17d155d437272a8b173bb516e2c251d0596441bdb", 12),
    "SRM 99b": ("99b", "52d58ff04cd31311879c9503d9846c80b4b22f67d52fa33bb8152bc0c4884535", 8),
}


def number(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
        raise ValueError("INVALID_REPORTED_NUMBER")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("INVALID_REPORTED_NUMBER") from exc
    return result


def validate(document, root, receipt):
    root = Path(root).resolve()
    if (document.get("schema_version") != "certified-elements-transcription-v1"
            or document.get("core_engine_eligible") is not False
            or document.get("training_release") is not False
            or document.get("evidence_kind") != "OBSERVED"
            or document.get("release_kind") != "INTERNAL_REFERENCE_NOT_PRODUCTION"):
        raise ValueError("REFERENCE_SCOPE_REQUIRED")
    source = receipt.get("sources", {}).get("nist-srm-ceramics", {})
    if (source.get("source_license") != "LicenseRef-NIST-NonSRD-Data-Use"
            or document.get("source_license") != source.get("source_license")
            or document.get("license_evidence") != source.get("license_evidence")
            or source.get("commercial_use_allowed") != "ALLOWED"
            or source.get("rights_partition") != "NIST_NON_SRD_REFERENCE"
            or "nist-srm-ceramics" in receipt.get("failures", {})):
        raise ValueError("UNREVIEWED_REFERENCE_RIGHTS")
    if document.get("columns") != ["element", "reported_value", "reported_uncertainty", "unit", "coverage_factor"]:
        raise ValueError("TRANSCRIPTION_COLUMNS_CHANGED")
    files = {f["sha256"]: f for f in receipt["files"] if f["source_id"] == "nist-srm-ceramics"}
    seen, total = set(), 0
    for record in document["records"]:
        code = record["product_code"]
        if code in seen or code not in REVIEWED:
            raise ValueError("UNREVIEWED_OR_DUPLICATE_CERTIFICATE")
        seen.add(code)
        slug, digest, count = REVIEWED[code]
        expected_url = f"https://tsapps.nist.gov/srmext/certificates/{slug}.pdf"
        if (record.get("raw_sha256") != digest or digest not in files
                or record.get("source_url") != expected_url or files[digest]["source_url"] != expected_url):
            raise ValueError("CERTIFICATE_PROVENANCE_MISMATCH")
        target = (root / files[digest]["raw_path"]).resolve()
        if not target.is_relative_to(root) or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("CERTIFICATE_HASH_MISMATCH")
        if (record.get("source_page") != 1 or record.get("source_table") != "Table 1"
                or record.get("certification_status") != "CERTIFIED_BY_SOURCE"):
            raise ValueError("CERTIFIED_TABLE_REQUIRED")
        if record.get("analysis_basis") not in ("DRY", "AS_RECEIVED", "UNKNOWN") or not record.get("basis_evidence"):
            raise ValueError("BASIS_EVIDENCE_REQUIRED")
        uncertainty = record.get("uncertainty_definition")
        if uncertainty not in ("EXPANDED_GUM", "NBS_95_95_TOLERANCE"):
            raise ValueError("UNCERTAINTY_DEFINITION_REQUIRED")
        elements = set()
        for row in record["measurements"]:
            if not isinstance(row, list) or len(row) != 5:
                raise ValueError("MALFORMED_MEASUREMENT")
            element, value, error, unit, factor = row
            if not isinstance(element, str) or not re.fullmatch(r"[A-Z][a-z]?", element) or element in elements:
                raise ValueError("INVALID_OR_DUPLICATE_ELEMENT")
            elements.add(element)
            if unit not in ("wt_pct", "mg/kg"):
                raise ValueError("UNSUPPORTED_UNIT")
            upper = Decimal("100") if unit == "wt_pct" else Decimal("1000000")
            if number(value) > upper or number(error) > upper:
                raise ValueError("OUT_OF_BOUNDS")
            if uncertainty == "EXPANDED_GUM":
                if number(factor) <= 0:
                    raise ValueError("COVERAGE_FACTOR_REQUIRED")
            elif factor is not None:
                raise ValueError("TOLERANCE_IS_NOT_EXPANDED_UNCERTAINTY")
        if len(elements) != count:
            raise ValueError("INCOMPLETE_CERTIFIED_TABLE")
        total += len(elements)
    if seen != set(REVIEWED):
        raise ValueError("INCOMPLETE_REFERENCE_SET")
    return {"validator_version": VERSION, "status": "VALIDATED_REFERENCE_STRUCTURE_AND_ARCHIVE",
            "materials": len(seen), "certified_element_values": total,
            "independently_double_checked_transcription": False,
            "production_ready_material_analyses": 0, "training_release": False,
            "limitations": ["Partial elemental data, not complete oxide chemistry.",
                            "No inference of LOI, oxidation state, missing values, or commercial product equivalence.",
                            "Certificate issue date is not measurement date.",
                            "Structural and checksum checks do not independently verify transcription accuracy."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcription", type=Path)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = json.loads(args.transcription.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    report = validate(document, args.storage, receipt)
    report["transcription_sha256"] = hashlib.sha256(args.transcription.read_bytes()).hexdigest()
    report["receipt_sha256"] = hashlib.sha256(args.receipt.read_bytes()).hexdigest()
    report["validator_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
