"""Write an immutable local research bundle; no online calls or UI claims."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
from uuid import uuid4

from .foundation import element_catalog, formula_report, oxide_equivalent, reaction_balance, OXIDES


def run(output_root):
    output = Path(output_root) / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    elements = element_catalog()
    oxides = [formula_report(formula, 100) for formula in OXIDES]
    examples = {
        "qualifier": "THEORETICAL_EXAMPLES_NOT_MEASURED_RECIPES",
        "formulas": [formula_report(f) for f in ("CaCO3", "CaMg(CO3)2", "Al2Si2O5(OH)4", "ZrSiO4")],
        "iron_reporting_basis_comparison": [oxide_equivalent("Fe", 10, oxide) for oxide in ("FeO", "Fe2O3")],
        "atom_balance_only": reaction_balance({"CaCO3": 1}, {"CaO": 1, "CO2": 1}),
    }
    payloads = {"elements.json": elements, "oxides.json": oxides, "examples.json": examples}
    for name, payload in payloads.items():
        with (output / name).open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
    with (output / "oxide-summary.csv").open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["formula", "molar_mass_g_mol", "constant_set_id", "qualifier"])
        writer.writeheader()
        writer.writerows({key: row[key] for key in writer.fieldnames} for row in oxides)
    summary = {
        "schema_version": "chemistry-research-bundle-v1", "created_at": datetime.now(timezone.utc).isoformat(),
        "element_count": len(elements), "standard_mass_available": sum(e["status"] == "AVAILABLE" for e in elements),
        "oxide_count": len(oxides), "new_real_material_analyses": 0,
        "limits": "Research stoichiometry only; no UMF/recipe engine, real glaze fit, phase equilibrium or fracture probability",
        "packages": {name: version(name) for name in ("periodictable", "pyparsing", "numpy")},
        "python": platform.python_version(),
        "source_code_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob("*.py")},
        "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir()},
    }
    with (output / "receipt.json").open("x", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
    return output, summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("storage/chemistry/runs"))
    args = parser.parse_args()
    output, summary = run(args.output_root)
    print(json.dumps({"output": str(output), **summary}, indent=2))
