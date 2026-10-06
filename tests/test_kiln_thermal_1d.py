"""Independent analytic limits and conservation, not physical clay validation."""
from copy import deepcopy
import json
import math
import unittest

from research.thermal.kiln_1d import SIGMA, ThermalInputError, simulate


def case(cells=16, dt=.01, end=.2):
    return {"schema_version": "kiln-thermal-1d-v1", "case_id": "analytic-slab",
            "area_m2": 1, "initial_temperature_c": 100, "max_step_s": dt,
            "layers": [{"layer_id": "body", "thickness_m": 2, "cells": cells,
                        "conductivity_w_m_k": 1, "density_kg_m3": 1, "specific_heat_j_kg_k": 1,
                        "valid_temperature_c": [0, 1800], "state": "INERT_SOLID_CONSTANT_PROPERTIES",
                        "source_ref": "fixture:analytic", "input_kind": "SYNTHETIC"}],
            "boundary": {side: {"h_w_m2_k": 1, "emissivity": 0, "source_ref": "fixture:analytic", "input_kind": "SYNTHETIC"}
                         for side in ("left", "right")},
            "schedule": {"basis": "PRESCRIBED_ENVIRONMENT", "input_kind": "SYNTHETIC",
                         "source_ref": "fixture:analytic", "points": [
                             {"time_s": 0, "gas_c": 0, "wall_c": 0},
                             {"time_s": end, "gas_c": 0, "wall_c": 0}]}}


def exact_convective_slab(x, time):
    # Half-width L=1, alpha=1, Bi=hL/k=1. Uniform initial 100 C, ambient 0 C.
    # Separation of variables: mu*tan(mu)=Bi, A=4sin(mu)/(2mu+sin(2mu)).
    terms = []
    for i in range(40):
        lo, hi = i*math.pi+1e-10, (i+.5)*math.pi-1e-10
        for _ in range(60):
            m = (lo+hi)/2
            if m*math.tan(m) > 1:
                hi = m
            else:
                lo = m
        mu = (lo+hi)/2
        terms.append(4*math.sin(mu)/(2*mu+math.sin(2*mu))*math.cos(mu*(x-1))*math.exp(-mu**2*time))
    return 100*sum(terms)


class KilnThermalTests(unittest.TestCase):
    def test_equilibrium_and_insulated_energy(self):
        c = case()
        for point in c["schedule"]["points"]:
            point.update(gas_c=100, wall_c=100)
        for face in c["boundary"].values():
            face["emissivity"] = .85
        r = simulate(c)
        for row in r["series"]:
            self.assertLess(max(abs(v-100) for v in row["cell_temperature_c"]), 1e-9)
        for face in c["boundary"].values():
            face.update(h_w_m2_k=0, emissivity=0)
        c["schedule"]["points"][-1].update(gas_c=1200, wall_c=1300)
        r = simulate(c)
        self.assertEqual(r["series"][-1]["cell_temperature_c"], [100.]*16)
        self.assertEqual(r["diagnostics"]["max_abs_energy_residual_j"], 0)

    def test_spatial_refinement_against_continuum_solution(self):
        errors = []
        for cells in (8, 16, 32):
            r = simulate(case(cells, .0005, .2))
            expected = [exact_convective_slab(x, .2) for x in r["mesh"]["cell_centers_m"]]
            errors.append(max(abs(a-b) for a, b in zip(expected, r["series"][-1]["cell_temperature_c"])))
        self.assertLess(errors[-1], .04)
        self.assertLess(errors[1], errors[0]*.5)
        self.assertLess(errors[2], errors[1]*.6)

    def test_time_refinement_against_continuum_solution(self):
        errors = []
        for dt in (.04, .02, .01):
            r = simulate(case(128, dt, .2))
            values = r["series"][-1]["cell_temperature_c"]
            expected = [exact_convective_slab(x, .2) for x in r["mesh"]["cell_centers_m"]]
            errors.append(max(abs(a-b) for a, b in zip(values, expected)))
        self.assertLess(errors[1], .65*errors[0])
        self.assertLess(errors[2], .65*errors[1])

    def test_radiation_face_balance_and_layered_steady_solution(self):
        c = case(8, .1, 10)
        c["initial_temperature_c"] = 40
        c["layers"][0].update(thickness_m=.05, conductivity_w_m_k=.5)
        second = deepcopy(c["layers"][0])
        second.update(layer_id="glaze", thickness_m=.01, conductivity_w_m_k=.1, cells=2)
        c["layers"].append(second)
        c["boundary"]["left"].update(h_w_m2_k=10, emissivity=0)
        c["boundary"]["right"].update(h_w_m2_k=0, emissivity=1)
        for p in c["schedule"]["points"]:
            p.update(gas_c=100, wall_c=0)
        # Independent series resistance solution: 1/h + L1/k1 + L2/k2 = .3 m2 K/W.
        lo, hi = 0., 100/.3
        for _ in range(100):
            q = (lo+hi)/2
            if q > SIGMA*((373.15-.3*q)**4-273.15**4):
                hi = q
            else:
                lo = q
        q = (lo+hi)/2
        r = simulate(c)
        final = r["series"][-1]
        self.assertAlmostEqual(final["left_surface_c"], 100-q/10, places=6)
        self.assertAlmostEqual(final["right_surface_c"], 100-.3*q, places=6)
        for x, t in zip(r["mesh"]["cell_centers_m"], final["cell_temperature_c"]):
            resistance = .1 + min(x, .05)/.5 + max(0, x-.05)/.1
            self.assertAlmostEqual(t, 100-q*resistance, places=6)
        self.assertLess(r["diagnostics"]["max_abs_energy_residual_j"], 2e-6)

    def test_single_cell_convection_has_exact_discrete_recurrence(self):
        c = case(1, .1, .1)
        c["layers"][0]["thickness_m"] = 1
        # C=1 J/K, each G=1/(1/h + halfwidth/k)=2/3 W/K.
        expected = 100/(1+.1*2*(2/3))
        r = simulate(c)
        self.assertAlmostEqual(r["series"][-1]["cell_temperature_c"][0], expected, places=8)

    def test_full_firing_knots_cooling_and_energy_ledger(self):
        c = case(8, 13, 60)
        c["initial_temperature_c"] = 20
        c["layers"][0].update(thickness_m=.02, conductivity_w_m_k=1, density_kg_m3=2000, specific_heat_j_kg_k=1000)
        for f in c["boundary"].values():
            f.update(h_w_m2_k=20, emissivity=.8)
        c["schedule"]["points"] = [dict(time_s=t, gas_c=v, wall_c=v) for t, v in [(0, 20), (601, 1200), (901, 1200), (2003, 20)]]
        r = simulate(c)
        times = [s["time_s"] for s in r["series"]]
        for t in (601, 901, 2003):
            self.assertIn(t, times)
        peak = r["series"][times.index(601)]
        self.assertLess(peak["layer_midpoint_c"]["body"], peak["right_surface_c"])
        final = r["series"][-1]
        self.assertGreater(final["layer_midpoint_c"]["body"], final["right_surface_c"])
        # ~10 MJ inputs: 1 mJ is a numerical ledger tolerance, not measurement uncertainty.
        self.assertLess(r["diagnostics"]["max_abs_energy_residual_j"], 1e-3)
        self.assertGreater(r["diagnostics"]["peak_spatial_temperature_span_c"], 0)

    def test_area_scaling_does_not_change_temperatures(self):
        c = case()
        a = simulate(c)["series"][-1]
        c["area_m2"] = 2
        b = simulate(c)["series"][-1]
        self.assertAlmostEqual(a["left_surface_c"], b["left_surface_c"], places=8)
        self.assertAlmostEqual(a["convective_energy_in_j"]*2, b["convective_energy_in_j"], places=7)

    def test_input_preserved_output_reproducible_and_scope_visible(self):
        c = case()
        original = deepcopy(c)
        a, b = simulate(c), simulate(c)
        self.assertEqual(c, original)
        self.assertEqual(a, b)
        self.assertTrue(a["contains_synthetic_inputs"])
        self.assertIsNone(a["uncertainty"])
        self.assertEqual(a["physical_validation"], "NOT_PERFORMED")
        json.dumps(a, allow_nan=False)

    def test_invalid_inputs_domains_and_size_limits(self):
        for key, value in [("area_m2", True), ("max_step_s", float("nan")), ("max_step_s", 1e-6), ("initial_temperature_c", -274)]:
            with self.subTest(key=key, value=value), self.assertRaises(ThermalInputError):
                c = case(); c[key] = value; simulate(c)
        for field, value in [("conductivity_w_m_k", 0), ("cells", True), ("valid_temperature_c", [0, 50]),
                             ("source_ref", ""), ("state", "RAW_CLAY"), ("input_kind", "VERIFIED")]:
            with self.subTest(field=field), self.assertRaises(ThermalInputError):
                c = case(); c["layers"][0][field] = value; simulate(c)
        c = case(); c["unexpected"] = 1
        with self.assertRaises(ThermalInputError):
            simulate(c)
        c = case(); c["schedule"]["points"][-1]["time_s"] = 0
        with self.assertRaises(ThermalInputError):
            simulate(c)
        c = case(); c["boundary"]["left"]["emissivity"] = 1.1
        with self.assertRaises(ThermalInputError):
            simulate(c)

    def test_material_scope_checks_surface_not_only_cell_centers(self):
        c = case(1, 1e-3, 1e-3)
        c["layers"][0]["valid_temperature_c"] = [0, 120]
        for p in c["schedule"]["points"]:
            p.update(gas_c=1200, wall_c=1200)
        with self.assertRaisesRegex(ThermalInputError, "OUT_OF_SURFACE_MATERIAL_DOMAIN"):
            simulate(c)


if __name__ == "__main__":
    unittest.main()
