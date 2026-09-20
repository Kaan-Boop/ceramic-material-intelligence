"""Export compact provenance/checksum inventory, not raw third-party records."""
import argparse
import hashlib
import json
from pathlib import Path


def build_inventory(root, profile):
    root, profile = Path(root).resolve(), Path(profile).resolve()
    if not profile.is_relative_to(root):
        raise ValueError("PROFILE_MUST_BE_WITHIN_STORAGE")
    files, sources, receipts = {}, {}, []
    for path in sorted((root / "receipts").glob("*.json"), key=lambda p: json.loads(p.read_text(encoding="utf-8"))["created_at"]):
        receipt = json.loads(path.read_text(encoding="utf-8"))
        sources.update(receipt["sources"])
        receipts.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "created_at": receipt["created_at"], "failures": receipt["failures"]})
        for item in receipt["files"]:
            if item["source_id"] not in receipt["sources"]:
                continue
            target = (root / item["raw_path"]).resolve()
            if not target.is_relative_to(root) or hashlib.sha256(target.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError("RAW_VERIFICATION_FAILED")
            files[(item["source_id"], item["filename"], item["sha256"])] = item
    report = json.loads((profile / "report.json").read_text(encoding="utf-8"))
    for source_id, source in sources.items():
        # Explicit metadata migration for early acquisition receipts; no chemistry changes.
        if source.get("license") not in ("CC-BY-4.0", "GPL-3.0-or-later") or source.get("commercial_use_allowed") not in ("ALLOWED", "ALLOWED_WITH_LICENSE_CONDITIONS"):
            raise ValueError("UNREVIEWED_RIGHTS_MIGRATION")
        source["source_url"] = source.get("source_url", source["license_evidence"])
        source["source_license"] = source.get("source_license", source["license"])
        source["commercial_use_allowed"] = "ALLOWED"
        source["attribution_required"] = "REQUIRED"
        source["share_alike_required"] = "REQUIRED" if source_id == "kiln-controller" else "NOT_REQUIRED"
        source["license_conditions"] = "Attribution and license retention required; GPL reference is separately partitioned, not relicensed. Product release remains NOT_APPROVED."
        source["rights_partition"] = "COPYLEFT_REFERENCE" if source_id == "kiln-controller" else "CC_BY_REFERENCE"
        source["layer"] = "OPEN_DATA"
    return {"schema_version": "research-inventory-v1", "release_kind": "INTERNAL_REFERENCE_NOT_PRODUCTION",
            "metadata_migration": "Early receipt boolean/conditional rights fields mapped to required enums; original receipts retained.",
            "source_count": len(sources), "unique_source_file_contents": len(files),
            "bytes_by_unique_source_file_content": sum(item["bytes"] for item in files.values()),
            "sources": sources, "receipts": receipts, "files": list(files.values()),
            "profile_directory": profile.relative_to(root).as_posix(), "quality_report": report,
            "profile_artifacts": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(profile.glob("*.json"))},
            "production_ready_material_analyses": 0, "external_publication": False, "training_release": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inventory = build_inventory(args.storage, args.profile)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(inventory, stream, ensure_ascii=False, indent=2)
    print(json.dumps({"output": str(args.output), "sources": inventory["source_count"], "files": inventory["unique_source_file_contents"]}))


if __name__ == "__main__":
    main()
