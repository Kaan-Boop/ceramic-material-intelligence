"""SI-unit, linear tetrahedral FEM. No file, network, or database access.

Sources and validity: docs/simulation/02_MODEL_SCOPE.md.
Numerical verification is not physical validation of ceramic properties.
"""
from dataclasses import dataclass
import numpy as np
from scipy.sparse.linalg import splu
from skfem import MeshTet, Basis, ElementTetP1, ElementVector, BilinearForm, LinearForm, condense, solve
from skfem.helpers import dot, grad, ddot, sym_grad, trace


def finite(value, name):
    if isinstance(value, (bool, str)) or not np.isfinite(value):
        raise ValueError(f"{name}: finite numeric value required")
    return float(value)


@dataclass(frozen=True)
class Material:
    name: str
    k_w_m_k: float
    density_kg_m3: float
    cp_j_kg_k: float
    young_pa: float
    poisson: float
    alpha_per_k: float
    valid_temperature_c: tuple
    source_ref: str
    state: str = "FIRED_SOLID_IDEALIZED"
    qualifier: str = "SYNTHETIC"

    def __post_init__(self):
        if self.state != "FIRED_SOLID_IDEALIZED":
            raise ValueError("UNSUPPORTED_MATERIAL_STATE: raw powder, melt and sintering are not solved")
        if self.qualifier != "SYNTHETIC":
            raise ValueError("Only explicitly SYNTHETIC properties are admitted in this research release")
        if not self.name or not self.source_ref:
            raise ValueError("Material identity and source_ref required")
        for name in ("k_w_m_k", "density_kg_m3", "cp_j_kg_k", "young_pa"):
            if finite(getattr(self, name), name) <= 0:
                raise ValueError(f"{name}: must be positive")
        nu = finite(self.poisson, "poisson")
        # Restrict this low-order displacement formulation away from locking.
        if not -0.9 < nu < 0.45:
            raise ValueError("poisson: supported interval is (-0.9, 0.45)")
        finite(self.alpha_per_k, "alpha_per_k")
        if len(self.valid_temperature_c) != 2:
            raise ValueError("valid_temperature_c: two endpoints required")
        lo, hi = [finite(v, "valid_temperature_c") for v in self.valid_temperature_c]
        if lo < -273.15 or lo >= hi:
            raise ValueError("Invalid temperature validity interval")

    def check_temperature(self, values):
        values = np.asarray(values, dtype=float)
        lo, hi = self.valid_temperature_c
        if not np.isfinite(values).all() or values.min() < lo - 1e-9 or values.max() > hi + 1e-9:
            raise ValueError(f"OUT_OF_DOMAIN: {self.name} temperature outside [{lo}, {hi}] degC")


@dataclass
class Domain:
    mesh: MeshTet
    basis: Basis
    materials: tuple
    region: np.ndarray

    def prop(self, name):
        return np.array([getattr(m, name) for m in self.materials])[self.region, None]

    def check_temperatures(self, values):
        values = np.asarray(values, dtype=float)
        if values.shape != (self.basis.N,):
            raise ValueError("Temperature field must contain one scalar per mesh node")
        for index, material in enumerate(self.materials):
            nodes = np.unique(self.mesh.t[:, self.region == index])
            material.check_temperature(values[nodes])


def make_domain(length_m, width_m, body_m, glaze_m, resolution, materials):
    dims = [finite(v, "geometry_m") for v in (length_m, width_m, body_m, glaze_m)]
    if min(dims) <= 0:
        raise ValueError("All geometry lengths must be positive SI metres")
    if len(resolution) != 4 or any(type(n) is not int or not 1 <= n <= 64 for n in resolution):
        raise ValueError("resolution: four integer subdivision counts, each in [1, 64]")
    nx, ny, nb, ng = resolution
    if (nx + 1) * (ny + 1) * (nb + ng + 1) > 20000:
        raise ValueError("RESEARCH_SIZE_LIMIT: at most 20000 nodes in this direct-solver prototype")
    if len(materials) != 2:
        raise ValueError("Exactly two material layers required")
    z = np.r_[np.linspace(0, body_m, nb + 1), np.linspace(body_m, body_m + glaze_m, ng + 1)[1:]]
    mesh = MeshTet.init_tensor(np.linspace(0, length_m, nx + 1), np.linspace(0, width_m, ny + 1), z)
    # A mesh plane is placed exactly at the material interface: no mixed cells.
    region = (mesh.p[2, mesh.t].mean(axis=0) > body_m).astype(int)
    return Domain(mesh, Basis(mesh, ElementTetP1(), intorder=2), tuple(materials), region)


@BilinearForm
def diffusion(u, v, w):
    return w.k * dot(grad(u), grad(v))


@BilinearForm
def capacity(u, v, w):
    return w.rho_cp * u * v


def heat_matrices(domain):
    basis = domain.basis
    return (diffusion.assemble(basis, k=domain.prop("k_w_m_k")),
            capacity.assemble(basis, rho_cp=domain.prop("density_kg_m3") * domain.prop("cp_j_kg_k")))


def steady_heat(domain, bottom_c, top_c):
    """Specified top/bottom temperatures; zero normal heat flux on sides."""
    bottom_c, top_c = finite(bottom_c, "bottom_c"), finite(top_c, "top_c")
    for m in domain.materials:
        m.check_temperature([bottom_c, top_c])
    basis = domain.basis
    z = domain.mesh.p[2]
    bottom, top = np.where(z == z.min())[0], np.where(z == z.max())[0]
    fixed = np.r_[bottom, top]
    prescribed = basis.zeros()
    prescribed[bottom], prescribed[top] = bottom_c, top_c
    k, _ = heat_matrices(domain)
    temperature = solve(*condense(k, np.zeros(basis.N), x=prescribed, D=fixed))
    domain.check_temperatures(temperature)
    reaction = k @ temperature
    free = np.setdiff1d(np.arange(basis.N), fixed)
    qbottom, qtop = float(reaction[bottom].sum()), float(reaction[top].sum())
    diagnostics = {
        "bottom_reaction_w": qbottom, "top_reaction_w": qtop,
        "boundary_power_imbalance_w": abs(qbottom + qtop),
        "boundary_power_imbalance_relative": (abs(qbottom + qtop) / max(abs(qbottom), abs(qtop)) if max(abs(qbottom), abs(qtop)) > 1e-10 else None),
        "relative_balance_unavailable_reason": ("NEGLIGIBLE_BOUNDARY_POWER" if max(abs(qbottom), abs(qtop)) <= 1e-10 else None),
        "free_heat_residual_w_l2": float(np.linalg.norm(reaction[free])),
    }
    return temperature, diagnostics


def transient_heat(domain, initial_c, boundary_c, dt_s, steps):
    """Backward Euler; constant temperature on ALL exterior faces.

    This is a separate prescribed-boundary benchmark, not a kiln heat-transfer model.
    Returns each step for numerical convergence checks; no convection/radiation.
    """
    boundary_c = finite(boundary_c, "boundary_c")
    if finite(dt_s, "dt_s") <= 0 or type(steps) is not int or not 1 <= steps <= 10000:
        raise ValueError("Positive dt_s and integer steps in [1, 10000] required")
    initial = np.asarray(initial_c, dtype=float).copy()
    domain.check_temperatures(initial)
    for m in domain.materials:
        m.check_temperature([boundary_c])
    fixed = domain.mesh.boundary_nodes()
    free = np.setdiff1d(np.arange(domain.basis.N), fixed)
    if not np.allclose(initial[fixed], boundary_c, atol=1e-10, rtol=0):
        raise ValueError("Initial field must match the imposed boundary temperature")
    if (steps + 1) * initial.size > 5_000_000:
        raise ValueError("RESEARCH_SIZE_LIMIT: transient history too large")
    k, mass = heat_matrices(domain)
    a = mass / dt_s + k
    factor = splu(a[free][:, free].tocsc()) if free.size else None
    history = [initial.copy()]
    for _ in range(steps):
        rhs = mass @ initial / dt_s
        initial[fixed] = boundary_c
        if factor is not None:
            initial[free] = factor.solve(rhs[free] - a[free][:, fixed] @ initial[fixed])
        domain.check_temperatures(initial)
        history.append(initial.copy())
    return np.asarray(history)


@BilinearForm
def stiffness(u, v, w):
    return 2 * w.mu * ddot(sym_grad(u), sym_grad(v)) + w.lam * trace(sym_grad(u)) * trace(sym_grad(v))


@LinearForm
def thermal_load(v, w):
    return (3 * w.lam + 2 * w.mu) * w.alpha * w.delta_t * trace(sym_grad(v))


def mechanical_constraints(domain, basis, support):
    mesh = domain.mesh
    if support == "ALL_NODES_FIXED":
        return np.arange(basis.N)
    if support != "RIGID_MODES_ONLY_321":
        raise ValueError("Unsupported mechanical support")
    # Three non-collinear corner points remove exactly six rigid-body modes.
    # No external support load is applied. Results at these pins need convergence checks.
    corners = [(0, 0, 0), (mesh.p[0].max(), 0, 0), (0, mesh.p[1].max(), 0)]
    nodes = []
    for corner in corners:
        matches = np.flatnonzero(np.all(mesh.p == np.asarray(corner)[:, None], axis=0))
        if len(matches) != 1:
            raise ValueError("Required reference corner missing")
        nodes.append(matches[0])
    return np.r_[basis.nodal_dofs[:, nodes[0]], basis.nodal_dofs[1:, nodes[1]], basis.nodal_dofs[2:, nodes[2]]]


def thermoelastic(domain, temperature_c, reference_c, support="RIGID_MODES_ONLY_321"):
    """Small-strain isotropic elasticity with perfectly bonded material interface."""
    reference_c = finite(reference_c, "reference_c")
    temperature = np.asarray(temperature_c, dtype=float)
    domain.check_temperatures(temperature)
    for m in domain.materials:
        m.check_temperature([reference_c])
    basis = Basis(domain.mesh, ElementVector(ElementTetP1()), intorder=2)
    young, nu, alpha = (domain.prop(n) for n in ("young_pa", "poisson", "alpha_per_k"))
    mu, lam = young / (2 * (1 + nu)), young * nu / ((1 + nu) * (1 - 2 * nu))
    delta_t = domain.basis.interpolate(temperature - reference_c)
    if np.max(np.abs(alpha * delta_t)) > .01:
        raise ValueError("OUT_OF_DOMAIN: thermal strain exceeds the research small-strain guard of 1%")
    k = stiffness.assemble(basis, mu=mu, lam=lam)
    f = thermal_load.assemble(basis, mu=mu, lam=lam, alpha=alpha, delta_t=delta_t)
    fixed = mechanical_constraints(domain, basis, support)
    free = np.setdiff1d(np.arange(basis.N), fixed)
    u = basis.zeros() if free.size == 0 else solve(*condense(k, f, D=fixed))
    if not np.isfinite(u).all():
        raise ValueError("SOLVER_FAILURE: non-finite displacement")
    gradient = basis.interpolate(u).grad
    strain = (gradient + gradient.swapaxes(0, 1)) / 2
    eye = np.eye(3)[:, :, None, None]
    elastic_strain = strain - eye * (alpha * delta_t)[None, None, :, :]
    stress = 2 * mu * elastic_strain + lam * eye * np.einsum("iieq->eq", elastic_strain)
    # Report cell averages; do not smooth a stress discontinuity across the interface.
    volume = basis.dx.sum(axis=1)
    stress_mean = np.einsum("ijeq,eq->eij", stress, basis.dx) / volume[:, None, None]
    principal = np.linalg.eigvalsh(stress_mean)
    energy = 0.5 * float(np.sum(np.einsum("ijeq,ijeq->eq", stress, elastic_strain) * basis.dx))
    residual = k @ u - f
    force_scale = max(float(np.linalg.norm(f)), 1e-20)
    reactions = np.zeros_like(residual)
    reactions[fixed] = residual[fixed]
    reaction_nodes = reactions[basis.nodal_dofs]
    return {
        "displacement_m": u[basis.nodal_dofs].T,
        "cell_stress_pa": stress_mean,
        "cell_max_principal_pa": principal[:, -1],
        "cell_volume_m3": volume,
        "diagnostics": {
            "support": support,
            "free_mechanical_residual_relative": float(np.linalg.norm(residual[free])) / force_scale,
            "reaction_resultant_n": reaction_nodes.sum(axis=1).tolist(),
            "reaction_moment_nm": np.cross(domain.mesh.p.T, reaction_nodes.T).sum(axis=0).tolist(),
            "elastic_energy_j": energy,
            "max_displacement_m": float(np.linalg.norm(u[basis.nodal_dofs], axis=0).max()),
            "cell_mean_max_principal_pa_by_layer": [float(np.average(principal[domain.region == i, -1], weights=volume[domain.region == i])) for i in range(2)],
        },
    }
