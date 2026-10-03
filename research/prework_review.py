"""Read a narrowly supported material literal WITHOUT executing attached code.

This is a review adapter, not a JavaScript interpreter or production importer.
It reuses the existing intake validator; it cannot grant rights or admit data.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re

from pipelines.ingestion.materials import validate_record

VERSION = "prework-review/1.0"
BLOCK = re.compile(r"^\s*const RAW_MATERIALS = \{\s*\n(.*?)^\s*\};", re.M | re.S)
ROW = re.compile(r'\s*([A-Za-z_][A-Za-z_0-9]*):\s*\{\s*name:\s*("(?:[^"\\]|\\.)*")\s*,\s*(.*?)\s*\}\s*,?\s*')
VALUE = re.compile(r"\s*([A-Za-z][A-Za-z0-9]*):\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*")


def review_attachment(raw: bytes, *, reviewed_on: str):
    if len(raw) > 2_000_000:
        raise ValueError("ATTACHMENT_TOO_LARGE")
    text = raw.decode("utf-8-sig")
    blocks = list(BLOCK.finditer(text))
    if len(blocks) != 1:
        raise ValueError("EXPECTED_ONE_SUPPORTED_MATERIAL_BLOCK")
    block = blocks[0]
    attachment_hash = hashlib.sha256(raw).hexdigest()
    source = dict(source_name="User-supplied CeramiSim preparation",
                  source_url="urn:sha256:" + attachment_hash,
                  source_type="USER_SUPPLIED_UNVERIFIED", source_author="UNKNOWN",
                  source_license="UNKNOWN", retrieval_date=reviewed_on,
                  commercial_use_allowed="UNKNOWN", attribution_required="UNKNOWN",
                  share_alike_required="UNKNOWN")
    # User authorized review of the attachment, not commercial reuse/training.
    rights = dict(derive="UNKNOWN", purposes=[], approved_analysis_hashes=[])
    candidates, seen = [], set()
    start_line = text.count("\n", 0, block.start(1)) + 1
    for offset, line in enumerate(block.group(1).splitlines()):
        if not line.strip():
            continue
        match = ROW.fullmatch(line)
        if not match:
            raise ValueError("UNSUPPORTED_MATERIAL_LITERAL")
        key, quoted_name, contents = match.groups()
        if key in seen:
            raise ValueError("DUPLICATE_MATERIAL")
        seen.add(key)
        oxides, numeric_literals, exact_range_issues = {}, {}, []
        for token in contents.split(","):
            value_match = VALUE.fullmatch(token)
            if not value_match:
                raise ValueError("UNSUPPORTED_OXIDE_LITERAL")
            oxide, numeric = value_match.groups()
            if oxide in oxides:
                raise ValueError("DUPLICATE_OXIDE")
            exact = Decimal(numeric)
            value = float(numeric)
            if not math.isfinite(value):
                raise ValueError("NON_FINITE_OXIDE")
            if exact != 0 and value == 0:
                raise ValueError("NUMERIC_UNDERFLOW")
            if not Decimal(0) <= exact <= Decimal(100):
                exact_range_issues.append(dict(code="INVALID_EXACT_OXIDE_PERCENTAGE",
                                               path="oxides." + oxide, severity="ERROR"))
            oxides[oxide] = value
            numeric_literals[oxide] = numeric
        record = dict(record_id=key, material_id=key, material_name=json.loads(quoted_name),
                      analysis_version=None, record_kind="REPORTED", analysis_date=None,
                      method=None, analysis_basis="UNKNOWN", coverage="UNKNOWN",
                      omitted_oxides_statement=None, oxides=oxides, loi_pct=None,
                      moisture_pct=None)
        status, issues, normalized = validate_record(record, source, rights, "INTERNAL_REFERENCE")
        if status == "accepted" or normalized is not None:
            raise ValueError("REVIEW_ADAPTER_MUST_NOT_ADMIT_UNVERIFIED_DATA")
        if exact_range_issues:
            status = "rejected"
            issues.extend(exact_range_issues)
        # Do not calculate a nominal composition total from rejected percentages.
        total = math.fsum(oxides.values()) if status != "rejected" else None
        candidates.append(dict(material_key=key, material_name=record["material_name"],
                               attachment_line=start_line + offset,
                               reported_oxides=oxides, reported_numeric_literals=numeric_literals,
                               reported_oxide_total=total,
                               difference_to_100_arithmetic_only=100 - total if total is not None else None,
                               analysis_basis="UNKNOWN", loi_pct=None, status=status,
                               issues=issues))
    if not candidates:
        raise ValueError("EMPTY_MATERIAL_BLOCK")
    return dict(schema_version=VERSION, reviewed_on=reviewed_on,
                attachment_sha256=attachment_hash, attachment_bytes=len(raw),
                scope="INTERNAL_REVIEW_ONLY_NOT_CATALOGUE_OR_TRAINING",
                source=source, candidates=candidates,
                counts=dict(received=len(candidates), accepted=0,
                            quarantined=sum(c["status"] == "quarantined" for c in candidates),
                            rejected=sum(c["status"] == "rejected" for c in candidates)),
                training_permission="UNKNOWN_NOT_APPROVED",
                source_code_executed=False, production_data_changed=False,
                limitations=["Literal parser is intentionally narrow; unsupported syntax stops review.",
                             "Difference from 100 is NOT a measured or inferred LOI.",
                             "Reported zero values are preserved, not scientifically verified.",
                             "Unreported oxides remain unknown; values are not normalized.",
                             "This does not validate the UI, model equations or legal rights."])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("attachment", type=Path)
    parser.add_argument("--reviewed-on", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = review_attachment(args.attachment.read_bytes(), reviewed_on=args.reviewed_on)
    if args.output:
        # Generated review artifact, never overwrite an earlier review.
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
    print(json.dumps(dict(counts=report["counts"], attachment_sha256=report["attachment_sha256"],
                          totals={r["material_key"]: r["reported_oxide_total"] for r in report["candidates"]}),
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
