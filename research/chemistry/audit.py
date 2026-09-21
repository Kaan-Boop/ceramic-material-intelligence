"""Reproducible offline quality checks; does not promote quarantined data."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

import periodictable.mass as upstream_mass
import periodictable.formulas as upstream_formulas

from .foundation import element_catalog, formula_report, OXIDES


def audit(root):
    root = Path(root).resolve()
    manifest_path = root / "data/manifests/chemistry-sources-2026-09-22.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_root = root / "storage/chemistry/01_sources"
    for entry in manifest["files"]:
        for key in ("raw_path", "readable_path"):
            path = (source_root / entry[key]).resolve()
            if not path.is_relative_to(source_root.resolve()):
                raise ValueError("SOURCE_PATH_OUTSIDE_ARCHIVE")
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError("SOURCE_CHECKSUM_MISMATCH")
    package_checks = {}
    for filename, module in (("periodictable/mass.py", upstream_mass), ("periodictable/formulas.py", upstream_formulas)):
        entry = next(f for f in manifest["files"] if f["source_id"] == "periodictable" and f["filename"] == filename)
        package_checks[filename] = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == entry["sha256"]
    if not all(package_checks.values()):
        raise ValueError("INSTALLED_SOURCE_DIFFERS_FROM_REVIEWED_ARCHIVE")
    data = json.loads((root / "data/reference/study-material-candidates-v1.json").read_text(encoding="utf-8"))
    records = data["records"]
    ids = [r["id"] for r in records]
    elements = element_catalog()
    errors = [abs(sum(formula_report(f, 100)["element_mass_g"].values()) - 100) for f in OXIDES]
    # Selected live CIAAW 2024 facts reviewed on 2026-09-22; not a complete new constant set.
    current_comparison = {"Zr": 91.222, "Gd": 157.249, "Lu": 174.96669}
    mass_by_symbol = {r["symbol"]: r["selected_molar_mass_g_mol"] for r in elements}
    return {
        "schema_version": "chemistry-quality-audit-v1", "grain": "One element identity / one theoretical oxide formula / one study material analysis candidate",
        "archive_sources": manifest["source_count"], "archive_files": len(manifest["files"]),
        "archive_checksum_checks_passed": True, "installed_source_matches": package_checks,
        "element_identities": len(elements), "unique_atomic_numbers": len({r["atomic_number"] for r in elements}),
        "standard_mass_available": sum(r["status"] == "AVAILABLE" for r in elements),
        "mass_unavailable": sum(r["status"] == "UNAVAILABLE" for r in elements),
        "oxide_formulas": len(OXIDES), "maximum_element_mass_balance_error_g_per_100g": max(errors),
        "study_candidates": len(records), "duplicate_candidate_ids": len(ids) - len(set(ids)),
        "accepted_study_materials": sum(r.get("core_engine_eligible") is True for r in records),
        "independently_counted_unknown_analysis_basis": sum(r.get("analysis_basis") == "UNKNOWN" for r in records),
        "quarantined_study_materials": sum(r.get("disposition") == "QUARANTINED" for r in records),
        "study_quality_flags": dict(Counter(flag for r in records for flag in r["quality_flags"])),
        "current_constant_comparison": {symbol: {"package": mass_by_symbol[symbol], "ciaaw_2024": value}
                                        for symbol, value in current_comparison.items()},
        "comparison_source": "https://ciaaw.org/atomic-weights.htm",
        "temporal_analysis": "No comparable repeated measurement series; no trend inferred",
        "limitations": ["No new real material analyses accepted", "Only three known constant revisions compared, not full CIAAW table validation",
                        "Numerical checks do not validate real firing behavior", "No input uncertainty propagation in stoichiometric results"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(Path(__file__).resolve().parents[2])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
