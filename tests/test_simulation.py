"""Analytic and invariant checks; not experimental material validation."""
import unittest
from dataclasses import replace
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
try:
    import numpy as np
    from research.simulation.core import Material, make_domain, steady_heat, transient_heat, thermoelastic
    FEM_AVAILABLE = True
except ModuleNotFoundError:
    FEM_AVAILABLE = False


@unittest.skipUnless(FEM_AVAILABLE, "Run with the isolated simulation environment")
class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.material = Material("Synthetic", 2., 2., 1., 1e9, .25, 1e-5, (0, 200), "fixture:test")

    def cube(self, n=3, second=None):
        return make_domain(1, 1, .5, .5, [n, n, n, n], [self.material, second or self.material])

    def test_layered_steady_solution_and_boundary_power(self):
        second = replace(self.material, k_w_m_k=4.)
        d = self.cube(second=second)
        t, diag = steady_heat(d, 20, 80)
        z = d.mesh.p[2]
        q = 60 / (.5 / 2 + .5 / 4)
        exact = 20 + q * (np.minimum(z, .5) / 2 + np.maximum(z - .5, 0) / 4)
        np.testing.assert_allclose(t, exact, atol=2e-10, rtol=0)
        self.assertAlmostEqual(diag["top_reaction_w"], q, places=9)
        self.assertLess(diag["boundary_power_imbalance_relative"], 1e-10)

    def test_zero_heat_flow_has_no_misleading_relative_error(self):
        _, diag = steady_heat(self.cube(), 20, 20)
        self.assertIsNone(diag["boundary_power_imbalance_relative"])
        self.assertLess(diag["boundary_power_imbalance_w"], 1e-10)

    def test_free_expansion_exact_displacement_zero_stress(self):
        d = self.cube()
        r = thermoelastic(d, np.full(d.basis.N, 80), 20)
        exact = (self.material.alpha_per_k * 60 * d.mesh.p).T
        np.testing.assert_allclose(r["displacement_m"], exact, atol=1e-13, rtol=0)
        self.assertLess(np.max(np.abs(r["cell_stress_pa"])), .01)
        self.assertLess(r["diagnostics"]["free_mechanical_residual_relative"], 1e-10)

    def test_all_fixed_hydrostatic_stress(self):
        d = self.cube()
        r = thermoelastic(d, np.full(d.basis.N, 80), 20, "ALL_NODES_FIXED")
        expected = -self.material.young_pa * self.material.alpha_per_k * 60 / (1 - 2 * self.material.poisson)
        np.testing.assert_allclose(r["cell_stress_pa"], np.broadcast_to(expected * np.eye(3), r["cell_stress_pa"].shape), atol=1e-8, rtol=1e-12)
        self.assertEqual(r["diagnostics"]["max_displacement_m"], 0.)

    def test_equal_cte_different_stiffness_stress_free(self):
        d = self.cube(second=replace(self.material, young_pa=3e9, poisson=.2))
        r = thermoelastic(d, np.full(d.basis.N, 80), 20)
        self.assertLess(np.max(np.abs(r["cell_stress_pa"])), .02)

    def test_zero_delta_t_zero_everything(self):
        d = self.cube()
        r = thermoelastic(d, np.full(d.basis.N, 20), 20)
        self.assertEqual(r["diagnostics"]["elastic_energy_j"], 0)
        self.assertEqual(r["diagnostics"]["max_displacement_m"], 0)

    def test_temperature_load_linear_and_energy_quadratic(self):
        d = self.cube(second=replace(self.material, alpha_per_k=2e-5))
        r1 = thermoelastic(d, np.full(d.basis.N, 40), 20)
        r2 = thermoelastic(d, np.full(d.basis.N, 60), 20)
        np.testing.assert_allclose(r2["displacement_m"], 2 * r1["displacement_m"], atol=1e-13)
        self.assertAlmostEqual(r2["diagnostics"]["elastic_energy_j"] / r1["diagnostics"]["elastic_energy_j"], 4., places=10)

    def test_transient_analytic_sine_mode_converges(self):
        errors = []
        for n in (3, 6):
            d = self.cube(n)
            phi = np.prod(np.sin(np.pi * d.mesh.p), axis=0)
            initial = 20 + phi
            initial[d.mesh.boundary_nodes()] = 20
            history = transient_heat(d, initial, 20, .00025, 40)
            exact = 20 + phi * np.exp(-3 * np.pi**2 * .01)  # k/(rho cp)=1
            errors.append(float(np.sqrt(np.mean((history[-1] - exact)**2))))
        self.assertLess(errors[1], errors[0] * .7)
        self.assertLess(errors[1], .02)

    def test_transient_constant_field_preserved(self):
        d = self.cube()
        out = transient_heat(d, np.full(d.basis.N, 30.), 30., .01, 3)
        np.testing.assert_allclose(out, 30., atol=1e-11)

    def test_invalid_materials(self):
        for changes in ({"young_pa": -1}, {"poisson": .5}, {"alpha_per_k": float("nan")}, {"state": "RAW_POWDER"}, {"qualifier": "MEASURED"}, {"source_ref": ""}, {"valid_temperature_c": (100, 20)}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(self.material, **changes)

    def test_out_of_range_temperatures_blocked(self):
        d = self.cube()
        with self.assertRaises(ValueError):
            steady_heat(d, 20, 1200)
        with self.assertRaises(ValueError):
            thermoelastic(d, np.full(d.basis.N, 30), 1200)

    def test_geometry_and_field_validation(self):
        with self.assertRaises(ValueError):
            make_domain(0, 1, .5, .5, [2]*4, [self.material]*2)
        with self.assertRaises(ValueError):
            make_domain(1, 1, .5, .5, [True]*4, [self.material]*2)
        with self.assertRaises(ValueError):
            thermoelastic(self.cube(), [30.], 20.)

    def test_nonphysical_scalar_types_and_large_strain_rejected(self):
        d = self.cube()
        for value in (True, "20", float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                steady_heat(d, value, 30)
        d = self.cube(second=replace(self.material, alpha_per_k=.001))
        with self.assertRaises(ValueError):
            thermoelastic(d, np.full(d.basis.N, 80), 20)

    def test_export_roundtrip_and_immutable_run_paths(self):
        from research.simulation.__main__ import run
        root = Path(__file__).resolve().parents[1]
        case = json.loads((root/"data/fixtures/simulation-bilayer-synthetic.json").read_text(encoding="utf-8"))
        case["resolution"] = [3,2,2,1]
        with tempfile.TemporaryDirectory() as tmp:
            first, second = run(deepcopy(case),tmp), run(deepcopy(case),tmp)
            self.assertNotEqual(first,second)
            report = json.loads((first/"result.json").read_text(encoding="utf-8"))
            report2 = json.loads((second/"result.json").read_text(encoding="utf-8"))
            self.assertEqual(report,report2)
            self.assertEqual(report["mesh_convergence"],"NOT_ESTABLISHED")
            fields = json.loads((first/"fields.json").read_text(encoding="utf-8"))
            self.assertEqual(len(fields["points"]),report["mesh"]["nodes"])
            self.assertEqual(len(fields["stress"]),report["mesh"]["tetrahedra"])
            vtk = (first/"fields.vtk").read_text(encoding="utf-8")
            self.assertIn("TENSORS stress_Pa double",vtk)
            page = (first/"index.html").read_text(encoding="utf-8")
            self.assertIn("SYNTHETIC",page)
            self.assertIn("Plotly.newPlot",page)
            self.assertNotIn('<script src="http',page)
            receipt = json.loads((first/"receipt.json").read_text(encoding="utf-8"))
            for item in receipt["files"]:
                self.assertEqual(hashlib.sha256((first/item["name"]).read_bytes()).hexdigest(),item["sha256"])


if __name__ == "__main__":
    unittest.main()
