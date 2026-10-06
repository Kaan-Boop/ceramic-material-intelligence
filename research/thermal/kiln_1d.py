"""Layered inert slab: finite-volume conduction with kiln convection/radiation.

Pure, SI, constant properties; no material defaults and no kinetics inferred
from a recipe. Method, domains and verification: docs/KILN_THERMAL_1D.md.
"""
from copy import deepcopy
import hashlib
import json
import math

VERSION = "layered-kiln-heat/0.1.0"
# Rounded CODATA value, W m^-2 K^-4. Fixed in the report for reproducibility.
SIGMA = 5.670374419e-8
MAX_STEPS = 20000


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


class ThermalInputError(ValueError):
    pass


def _fields(value, names, path):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ThermalInputError("INVALID_FIELDS:" + path)


def _num(value, low, high, path):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ThermalInputError("INVALID_NUMBER:" + path)
    return float(value)


def _text(value, path):
    if not isinstance(value, str) or not value.strip() or len(value) > 500:
        raise ThermalInputError("SOURCE_OR_ID_REQUIRED:" + path)


def _provenance(value):
    _text(value["source_ref"], "source_ref")
    if value["input_kind"] not in ("SYNTHETIC", "REPORTED", "MEASURED"):
        raise ThermalInputError("INVALID_INPUT_KIND")


def _prepare(case):
    _fields(case, "schema_version case_id layers area_m2 initial_temperature_c boundary schedule max_step_s", "case")
    if case["schema_version"] != "kiln-thermal-1d-v1":
        raise ThermalInputError("UNSUPPORTED_SCHEMA")
    _text(case["case_id"], "case_id")
    area = _num(case["area_m2"], 1e-8, 100, "area_m2")
    initial = _num(case["initial_temperature_c"], -273.14, 1800, "initial_temperature_c") + 273.15
    dt = _num(case["max_step_s"], 1e-6, 3600, "max_step_s")
    layers = case["layers"]
    if not isinstance(layers, list) or not 1 <= len(layers) <= 8:
        raise ThermalInputError("LAYER_COUNT_1_TO_8")
    dx, conductivity, capacity, positions, indices, bounds = [], [], [], [], [], []
    offset = 0.
    ids = set()
    for index, layer in enumerate(layers):
        _fields(layer, "layer_id thickness_m cells conductivity_w_m_k density_kg_m3 specific_heat_j_kg_k valid_temperature_c state source_ref input_kind", "layer")
        _text(layer["layer_id"], "layer_id")
        if layer["layer_id"] in ids:
            raise ThermalInputError("DUPLICATE_LAYER_ID")
        ids.add(layer["layer_id"])
        _provenance(layer)
        if layer["state"] != "INERT_SOLID_CONSTANT_PROPERTIES":
            raise ThermalInputError("INERT_SOLID_REQUIRED_NO_PHASE_CHANGE_MODEL")
        thickness = _num(layer["thickness_m"], 1e-6, 10, "thickness_m")
        n = layer["cells"]
        if type(n) is not int or not 1 <= n <= 256:
            raise ThermalInputError("INVALID_CELL_COUNT")
        k = _num(layer["conductivity_w_m_k"], 1e-4, 1e4, "conductivity_w_m_k")
        rho = _num(layer["density_kg_m3"], 1e-3, 1e5, "density_kg_m3")
        cp = _num(layer["specific_heat_j_kg_k"], 1e-3, 1e5, "specific_heat_j_kg_k")
        domain = layer["valid_temperature_c"]
        if not isinstance(domain, list) or len(domain) != 2:
            raise ThermalInputError("TEMPERATURE_DOMAIN_REQUIRED")
        lo, hi = [_num(v, -273.14, 1800, "valid_temperature_c") + 273.15 for v in domain]
        if lo >= hi or not lo <= initial <= hi:
            raise ThermalInputError("OUT_OF_MATERIAL_DOMAIN")
        for cell in range(n):
            dx.append(thickness / n)
            conductivity.append(k)
            capacity.append(rho * cp * thickness / n * area)
            positions.append(offset + (cell + .5) * thickness / n)
            indices.append(index)
            bounds.append((lo, hi))
        offset += thickness
    if len(dx) > 256:
        raise ThermalInputError("TOTAL_CELLS_LIMIT_256")
    boundary = case["boundary"]
    _fields(boundary, "left right", "boundary")
    for face in boundary.values():
        _fields(face, "h_w_m2_k emissivity source_ref input_kind", "boundary.face")
        _provenance(face)
        _num(face["h_w_m2_k"], 0, 1e5, "h_w_m2_k")
        _num(face["emissivity"], 0, 1, "emissivity")
    schedule = case["schedule"]
    _fields(schedule, "basis source_ref input_kind points", "schedule")
    _provenance(schedule)
    if schedule["basis"] not in ("PRESCRIBED_ENVIRONMENT", "MEASURED_ENVIRONMENT"):
        raise ThermalInputError("EXPLICIT_GAS_AND_WALL_TEMPERATURES_REQUIRED")
    if schedule["basis"] == "MEASURED_ENVIRONMENT" and schedule["input_kind"] != "MEASURED":
        raise ThermalInputError("MEASURED_ENVIRONMENT_REQUIRES_MEASURED_INPUT")
    points = schedule["points"]
    if not isinstance(points, list) or not 2 <= len(points) <= 1001:
        raise ThermalInputError("SCHEDULE_COUNT_2_TO_1001")
    for i, point in enumerate(points):
        _fields(point, "time_s gas_c wall_c", "schedule.point")
        _num(point["time_s"], 0, 1e7, "time_s")
        for key in ("gas_c", "wall_c"):
            _num(point[key], -273.14, 1800, key)
        if (i == 0 and point["time_s"] != 0) or (i > 0 and point["time_s"] <= points[i-1]["time_s"]):
            raise ThermalInputError("TIME_START_ZERO_THEN_STRICTLY_INCREASE")
    steps = sum(math.ceil((b["time_s"]-a["time_s"])/dt) for a, b in zip(points, points[1:]))
    if steps > MAX_STEPS or (steps+1)*len(dx) > 2_000_000:
        raise ThermalInputError("SIMULATION_SIZE_LIMIT")
    g = [area/(dx[i]/(2*conductivity[i])+dx[i+1]/(2*conductivity[i+1])) for i in range(len(dx)-1)]
    return area, initial, dt, dx, conductivity, capacity, positions, indices, bounds, g


def _surface(cell_k, gas_k, wall_k, half_conductance, h, emissivity):
    """Zero-capacity physical face, including half-cell conduction resistance.

    Returns surface K, incoming convection/radiation W/m2 and dq_in/dT_cell.
    A monotone scalar solve retains T^4 exactly, without a fixed radiation h.
    """
    if h == 0 and emissivity == 0:
        return cell_k, 0., 0., 0.
    lo, hi = min(cell_k, gas_k, wall_k), max(cell_k, gas_k, wall_k)
    s = cell_k
    for _ in range(80):
        s = (lo + hi)/2
        residual = half_conductance*(s-cell_k) - h*(gas_k-s) - emissivity*SIGMA*(wall_k**4-s**4)
        if residual > 0:
            hi = s
        else:
            lo = s
        if hi-lo < 1e-11:
            break
    derivative = h + 4*emissivity*SIGMA*s**3
    return (s, h*(gas_k-s), emissivity*SIGMA*(wall_k**4-s**4),
            -half_conductance*derivative/(half_conductance+derivative))


def _tridiagonal(diagonal, off, rhs):
    """Thomas solve, strictly diagonally dominant heat Jacobian (positive C/dt)."""
    d, b = diagonal.copy(), rhs.copy()
    for i in range(1, len(d)):
        ratio = off[i-1]/d[i-1]
        d[i] -= ratio*off[i-1]
        b[i] -= ratio*b[i-1]
    x = [0.]*len(d)
    x[-1] = b[-1]/d[-1]
    for i in range(len(d)-2, -1, -1):
        x[i] = (b[i]-off[i]*x[i+1])/d[i]
    return x


def simulate(case):
    """Integrate piecewise-linear gas/wall history; return explicit energy ledger.

    Backward Euler lands on every schedule knot, with Newton iterations for
    surface radiation. A converged algebraic residual is NOT a time-error bound.
    """
    area, initial, max_dt, dx, k, c, x, regions, bounds, g = _prepare(case)
    n = len(c)
    faces = case["boundary"]
    temperature = [initial]*n
    history = []
    cumulative_conv, cumulative_rad = 0., 0.
    max_cell_residual = 0.
    points = case["schedule"]["points"]

    def surfaces(t, gas, wall):
        return [_surface(t[i], gas, wall, 2*k[i]/dx[i], faces[side]["h_w_m2_k"], faces[side]["emissivity"])
                for i, side in ((0, "left"), (n-1, "right"))]

    def check_domain(t, surface):
        for v, (lo, hi) in zip(t, bounds):
            if not math.isfinite(v) or not lo-1e-9 <= v <= hi+1e-9:
                raise ThermalInputError("OUT_OF_MATERIAL_DOMAIN")
        for face, i in zip(surface, (0, n-1)):
            if not bounds[i][0]-1e-9 <= face[0] <= bounds[i][1]+1e-9:
                raise ThermalInputError("OUT_OF_SURFACE_MATERIAL_DOMAIN")

    def state(time, gas, wall, surface, iterations, residual):
        sensible = math.fsum(ci*(ti-initial) for ci, ti in zip(c, temperature))
        row = {"time_s": time, "gas_c": gas-273.15, "wall_c": wall-273.15,
               "cell_temperature_c": [v-273.15 for v in temperature],
               "left_surface_c": surface[0][0]-273.15, "right_surface_c": surface[1][0]-273.15,
               "heat_capacity_weighted_mean_c": math.fsum(ci*ti for ci, ti in zip(c, temperature))/sum(c)-273.15,
               "spatial_temperature_span_c": max(*temperature, surface[0][0], surface[1][0])-min(*temperature, surface[0][0], surface[1][0]),
               "convective_energy_in_j": cumulative_conv, "radiative_energy_in_j": cumulative_rad,
               "sensible_energy_change_j": sensible,
               "energy_residual_j": cumulative_conv+cumulative_rad-sensible,
               "nonlinear_iterations": iterations, "max_cell_balance_residual_w": residual}
        # Probe uses interpolation of cell-centre values at each layer midpoint.
        # This is a spatial probe, not an independent measurement.
        probes = {}
        for i, layer in enumerate(case["layers"]):
            cells = [j for j in range(n) if regions[j] == i]
            mid = len(cells)//2
            value = temperature[cells[mid]] if len(cells)%2 else (temperature[cells[mid-1]]+temperature[cells[mid]])/2
            probes[layer["layer_id"]] = value-273.15
        row["layer_midpoint_c"] = probes
        return row

    surface = surfaces(temperature, points[0]["gas_c"]+273.15, points[0]["wall_c"]+273.15)
    check_domain(temperature, surface)
    history.append(state(0., points[0]["gas_c"]+273.15, points[0]["wall_c"]+273.15, surface, 0, 0.))
    for a, b in zip(points, points[1:]):
        count = math.ceil((b["time_s"]-a["time_s"])/max_dt)
        dt = (b["time_s"]-a["time_s"])/count
        for step in range(1, count+1):
            fraction = step/count
            time = b["time_s"] if step == count else a["time_s"]+step*dt
            gas = a["gas_c"]+(b["gas_c"]-a["gas_c"])*fraction+273.15
            wall = a["wall_c"]+(b["wall_c"]-a["wall_c"])*fraction+273.15
            old = temperature.copy()

            def equations(t):
                boundary = surfaces(t, gas, wall)
                residual = [c[i]/dt*(t[i]-old[i]) for i in range(n)]
                diagonal = [ci/dt for ci in c]
                for i, conductance in enumerate(g):
                    outgoing = conductance*(t[i]-t[i+1])
                    residual[i] += outgoing
                    residual[i+1] -= outgoing
                    diagonal[i] += conductance
                    diagonal[i+1] += conductance
                for i, face in zip((0, n-1), boundary):
                    residual[i] -= area*(face[1]+face[2])
                    diagonal[i] -= area*face[3]
                return residual, diagonal, boundary

            for iteration in range(1, 41):
                residual, diagonal, surface = equations(temperature)
                norm = max(abs(v) for v in residual)
                scale = max(1., sum(abs(c[i]/dt*(temperature[i]-old[i])) for i in range(n)),
                            area*sum(abs(f[1])+abs(f[2]) for f in surface))
                if norm <= 1e-8 + 1e-10*scale:
                    break
                correction = _tridiagonal(diagonal, [-v for v in g], [-v for v in residual])
                # Damping also prevents nonphysical absolute temperatures during Newton iterations.
                for cut in range(30):
                    factor = .5**cut
                    trial = [v+factor*d for v, d in zip(temperature, correction)]
                    if min(trial) <= 0 or not all(math.isfinite(v) for v in trial):
                        continue
                    if max(abs(v) for v in equations(trial)[0]) < norm:
                        temperature = trial
                        break
                else:
                    raise ThermalInputError("NONLINEAR_SOLVER_FAILED_REDUCE_STEP")
            else:
                raise ThermalInputError("NONLINEAR_SOLVER_FAILED_REDUCE_STEP")
            check_domain(temperature, surface)
            max_cell_residual = max(max_cell_residual, norm)
            cumulative_conv += dt*area*sum(face[1] for face in surface)
            cumulative_rad += dt*area*sum(face[2] for face in surface)
            history.append(state(time, gas, wall, surface, iteration, norm))
    snapshot = deepcopy(case)
    kinds = [l["input_kind"] for l in case["layers"]] + [f["input_kind"] for f in faces.values()] + [case["schedule"]["input_kind"]]
    return {"schema_version": "kiln-thermal-1d-report-v1", "engine_version": VERSION,
            "status": "AVAILABLE", "evidence_kind": "PREDICTED", "method_kind": "DETERMINISTIC",
            "qualifier": "IDEALIZED_INERT_SLAB", "contains_synthetic_inputs": "SYNTHETIC" in kinds,
            "physical_validation": "NOT_PERFORMED", "uncertainty": None,
            "input_snapshot": snapshot, "input_hash": _digest({"version": VERSION, "input": snapshot, "sigma": SIGMA}),
            "constants": {"stefan_boltzmann_w_m2_k4": SIGMA},
            "mesh": {"cell_centers_m": x, "cell_widths_m": dx, "layer_indices": regions},
            "series": history,
            "diagnostics": {"steps": len(history)-1, "cells": n,
                            "max_cell_balance_residual_w": max_cell_residual,
                            "max_abs_energy_residual_j": max(abs(row["energy_residual_j"]) for row in history),
                            "peak_spatial_temperature_span_c": max(row["spatial_temperature_span_c"] for row in history)},
            "unavailable_sections": {"reaction_conversion": "KINETICS_NOT_COUPLED", "melt_fraction": "NO_PHASE_MODEL",
                                     "sintering": "NO_DENSIFICATION_MODEL", "defect_probability": "NO_CALIBRATED_MODEL"},
            "limitations": ["Plane slab; insulated edges; perfect thermal contact between layers.",
                            "Constant supplied conductivity, density and sensible heat capacity; fixed mass and geometry.",
                            "Grey diffuse surfaces inside large isothermal surroundings, view factor 1, nonparticipating gas.",
                            "Gas and wall temperatures are separate prescribed inputs, not a kiln controller or power model.",
                            "No drying, reaction energy, phase change, radiation inside the solid or mechanical coupling.",
                            "Source refs and MEASURED/REPORTED are user declarations, not data admission or physical validation.",
                            "Algebraic energy balance is not a discretization error or an experimental accuracy estimate."]}
