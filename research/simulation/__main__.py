import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
from uuid import uuid4
import numpy as np
from . import ENGINE_VERSION
from .core import Material, make_domain, steady_heat, thermoelastic
from .export import write_viewer, write_vtk


def solve_case(case):
    if case.get("schema_version") != "simulation-research-v1":
        raise ValueError("Unsupported simulation case schema")
    geometry = case["geometry_m"]
    domain = make_domain(*(geometry[k] for k in ("length", "width", "body_thickness", "glaze_thickness")), case["resolution"], [Material(**m) for m in case["materials"]])
    thermal = case["thermal"]
    temperature, heat = steady_heat(domain, thermal["bottom_c"], thermal["top_c"])
    mechanics = thermoelastic(domain, temperature, thermal["reference_c"], case["support"])
    return domain, temperature, heat, mechanics


def run(case, output_root):
    canonical = json.dumps(case, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    input_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    domain, temperature, heat, mechanics = solve_case(case)
    code_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob("*.py"))}
    report = {"schema_version":"simulation-report-v1", "engine_version":ENGINE_VERSION,
        "evidence_kind":"PREDICTED", "method_kind":"DETERMINISTIC", "qualifier":["SYNTHETIC","IDEALIZED"],
        "status":"AVAILABLE", "physical_validation":"NOT_PERFORMED", "mesh_convergence":"NOT_ESTABLISHED", "input_sha256":input_hash,
        "code_sha256":code_hashes, "solver_versions":{p:version(p) for p in ("scikit-fem","numpy","scipy","plotly")},
        "input_snapshot":case, "mesh":{"nodes":int(domain.mesh.nvertices),"tetrahedra":int(domain.mesh.nelements)},
        "heat":heat,"mechanics":mechanics["diagnostics"],
        "unavailable_sections":{"raw_to_fired_chemistry":"NO_VALIDATED_REACTION_KINETICS_OR_PHASE_DATABASE", "failure_probability":"NO_STRENGTH_DISTRIBUTION_OR_CALIBRATION", "sintering":"NO_DENSIFICATION_MODEL", "viscoelasticity":"NO_RELAXATION_MODEL", "radiation_convection":"PRESCRIBED_BOUNDARY_TEMPERATURES_ONLY"},
        "assumptions":["Two constant-property, isotropic, perfectly bonded fired solids", "Small strain; stress-free at the reference temperature", "Quasistatic mechanical response; no initial residual stress", "Dirichlet top/bottom temperature; insulated sides; no kiln boundary model", "No pores, cracks, melting, shrinkage kinetics or interface reactions"],
        "limitations":["Not a firing, crazing or food-safety prediction", "Cell-average stresses; corner peaks are not mesh-independent failure metrics", "No empirical confidence interval; unknown uncertainty is not zero"]}
    fields = {"units":{"points":"m","temperature":"degC","displacement":"m","stress":"Pa"},
        "points":domain.mesh.p.T.tolist(),"tetrahedra":domain.mesh.t.T.tolist(),"material_id":domain.region.tolist(),
        "temperature":temperature.tolist(),"displacement":mechanics["displacement_m"].tolist(),"stress":mechanics["cell_stress_pa"].tolist()}
    output = Path(output_root) / (input_hash[:12] + "-" + uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    for name, value in (("input.json",case),("result.json",report),("fields.json",fields)):
        (output/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False),encoding="utf-8")
    write_vtk(output/"fields.vtk",domain,temperature,mechanics)
    write_viewer(output/"index.html",case,domain,temperature,mechanics,report)
    receipt = {"generated_at":datetime.now(timezone.utc).isoformat(), "files":[{"name":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(output.iterdir())]}
    (output/"receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic 3D thermoelastic research; not a kiln controller")
    parser.add_argument("case",type=Path)
    parser.add_argument("--output",type=Path,default=Path("storage/simulation/03_runs"))
    args = parser.parse_args()
    try:
        print(run(json.loads(args.case.read_text(encoding="utf-8")), args.output).resolve())
    except (ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"INVALID_OR_UNSUPPORTED_CASE: {error}\n")
