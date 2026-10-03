"""Reproducible numerical verification receipt and one-at-a-time sensitivity."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import numpy as np
from .__main__ import solve_case
from .core import Material, make_domain, steady_heat, transient_heat, thermoelastic


def verify(case):
    rows = []
    for resolution in ([6,3,2,1], [12,6,4,2], [24,12,8,4]):
        current = deepcopy(case)
        current["resolution"] = resolution
        d, t, h, r = solve_case(current)
        rows.append({"resolution":resolution,"nodes":int(d.mesh.nvertices),"elements":int(d.mesh.nelements),**r["diagnostics"]})
    sensitivity = []
    # Hypothetical perturbations, not measured parameter distributions or confidence intervals.
    for label, location, factor in (("glaze_alpha_minus_10pct","alpha_per_k",.9),("glaze_alpha_plus_10pct","alpha_per_k",1.1),("glaze_E_minus_10pct","young_pa",.9),("glaze_E_plus_10pct","young_pa",1.1)):
        current = deepcopy(case)
        current["materials"][1][location] *= factor
        _, _, _, r = solve_case(current)
        sensitivity.append({"scenario":label,"factor":factor,**r["diagnostics"]})
    m = Material("Synthetic benchmark",2.,2.,1.,1e9,.25,1e-5,(0,200),"fixture:analytic-benchmarks")
    patch = make_domain(1,1,.5,.5,[3,3,3,3],[m,m])
    free = thermoelastic(patch,np.full(patch.basis.N,80.),20.)
    exact_u = (1e-5 * 60 * patch.mesh.p).T
    clamped = thermoelastic(patch,np.full(patch.basis.N,80.),20.,"ALL_NODES_FIXED")
    expected_stress = -1e9 * 1e-5 * 60 / (1-2*.25) * np.eye(3)
    m2 = Material("Synthetic conductor",4.,2.,1.,1e9,.25,1e-5,(0,200),"fixture:analytic-benchmarks")
    slab = make_domain(1,1,.5,.5,[3,3,3,3],[m,m2])
    t, heat = steady_heat(slab,20,80)
    z = slab.mesh.p[2]
    exact_t = 20 + 160 * (np.minimum(z,.5)/2 + np.maximum(z-.5,0)/4)
    transient = []
    for n in (3,6,9):
        d = make_domain(1,1,.5,.5,[n,n,n,n],[m,m])
        phi = np.prod(np.sin(np.pi*d.mesh.p),axis=0)
        initial = 20 + phi
        initial[d.mesh.boundary_nodes()] = 20
        out = transient_heat(d,initial,20,.00025,40)
        exact = 20 + phi * np.exp(-3*np.pi**2*.01)
        transient.append({"n":n,"dt_s":.00025,"rms_error_c":float(np.sqrt(np.mean((out[-1]-exact)**2)))})
    checks = {
        "free_expansion_max_displacement_error_m":float(np.abs(free["displacement_m"]-exact_u).max()),
        "free_expansion_max_absolute_stress_pa":float(np.abs(free["cell_stress_pa"]).max()),
        "fully_restrained_max_stress_error_pa":float(np.abs(clamped["cell_stress_pa"]-expected_stress).max()),
        "layered_heat_max_temperature_error_c":float(np.abs(t-exact_t).max()),
        "layered_heat_boundary_power_error_relative":heat["boundary_power_imbalance_relative"]}
    energy_change = abs(rows[-1]["elastic_energy_j"] / rows[-2]["elastic_energy_j"] - 1)
    stress_change = abs(rows[-1]["cell_mean_max_principal_pa_by_layer"][1]/rows[-2]["cell_mean_max_principal_pa_by_layer"][1]-1)
    passed = checks["free_expansion_max_displacement_error_m"] < 1e-12 and checks["free_expansion_max_absolute_stress_pa"] < .01 and checks["fully_restrained_max_stress_error_pa"] < .01 and checks["layered_heat_max_temperature_error_c"] < 1e-9 and checks["layered_heat_boundary_power_error_relative"] < 1e-10 and transient[-1]["rms_error_c"] < transient[0]["rms_error_c"]
    return {"schema_version":"simulation-verification-v1","generated_at":datetime.now(timezone.utc).isoformat(),
        "classification":{"evidence_kind":"CALCULATED","method_kind":"DETERMINISTIC","qualifier":"NUMERICAL_VERIFICATION_ONLY"},
        "input_snapshot":case,"source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob("*.py"))},
        "versions":{p:version(p) for p in ("scikit-fem","numpy","scipy")},"analytic_checks":checks,"analytic_passed":bool(passed),
        "transient_space_refinement":transient,"bilayer_mesh_refinement":rows,
        "mesh_comparison":{"last_energy_relative_change":energy_change,"last_glaze_mean_principal_relative_change":stress_change,"not_an_error_bound":True,"peak_stress_convergence_not_claimed":True},
        "sensitivity":{"method":"OAT +/-10% assumed perturbations; not statistical uncertainty", "baseline":rows[1],"scenarios":sensitivity},
        "physical_validation":"NOT_PERFORMED"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    report = verify(json.loads(args.case.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({"analytic_passed":report["analytic_passed"],"analytic_checks":report["analytic_checks"],"mesh_comparison":report["mesh_comparison"]},indent=2))
    if not report["analytic_passed"]:
        raise SystemExit(1)
