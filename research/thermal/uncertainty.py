"""Synthetic uncertainty propagation, not a fracture probability model.

Independent uniform whole-curve CTE offsets; temperatures and length are fixed.
See docs/THERMAL_UNCERTAINTY.md for scope and verification.
"""
from dataclasses import asdict, replace
import hashlib
import itertools
import json
import random
import statistics

from .core import Scenario, ModelInputError, calculate, finite, MODEL_VERSION as THERMAL_MODEL_VERSION

MODEL_VERSION = "synthetic-independent-uniform-cte/0.1.0"


def propagate(scenario: Scenario, *, glaze_half_width_per_k: float,
              body_half_width_per_k: float, samples: int, seed: int) -> dict:
    """Propagate declared synthetic assumptions, never infer distributions.

    Each draw shifts an entire alpha(T) curve by one constant. Thus points
    within a curve share the offset; offsets between materials are independent.
    Invalid support aborts the run; samples are not clipped or resampled.
    """
    if scenario.glaze.data_kind != "SYNTHETIC" or scenario.body.data_kind != "SYNTHETIC":
        raise ModelInputError("SYNTHETIC_ONLY", "scenario")
    widths = [finite(glaze_half_width_per_k, "glaze_half_width_per_k"),
              finite(body_half_width_per_k, "body_half_width_per_k")]
    if min(widths) < 0:
        raise ModelInputError("NONNEGATIVE_REQUIRED", "half_width")
    if type(samples) is not int or not 100 <= samples <= 100_000:
        raise ModelInputError("INTEGER_100_TO_100000_REQUIRED", "samples")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ModelInputError("UINT32_REQUIRED", "seed")
    baseline = calculate(scenario)

    def shifted(g, b):
        return replace(scenario, glaze=scenario.glaze.shifted(g), body=scenario.body.shifted(b))

    # The model is linear in these offsets. Checking all support corners
    # also checks the extreme per-material integrated strains.
    corners = [calculate(shifted(g, b)) for g, b in itertools.product(
        (-widths[0], widths[0]), (-widths[1], widths[1]))]
    key = "mismatch_strain_glaze_minus_body"
    rng = random.Random(seed)  # Does not alter global random state.
    values = sorted(calculate(shifted(rng.uniform(-widths[0], widths[0]),
                                      rng.uniform(-widths[1], widths[1])))[key]
                    for _ in range(samples))

    def quantile(p):
        position = (len(values) - 1) * p
        lower = int(position)
        upper = min(lower + 1, len(values) - 1)
        return values[lower] + (values[upper] - values[lower]) * (position - lower)

    snapshot = {"scenario": asdict(scenario), "glaze_half_width_per_k": widths[0],
                "body_half_width_per_k": widths[1], "samples": samples, "seed": seed,
                "model_version": MODEL_VERSION, "thermal_model_version": THERMAL_MODEL_VERSION}
    digest = hashlib.sha256(json.dumps(snapshot, sort_keys=True, allow_nan=False,
                                       separators=(",", ":")).encode()).hexdigest()
    dt = scenario.target_temperature_c - scenario.reference_temperature_c
    return {
        "model_version": MODEL_VERSION, "input_snapshot": snapshot, "input_hash": digest,
        "evidence_kind": "PREDICTED", "method_kind": "STATISTICAL",
        "qualifiers": ["SYNTHETIC", "ASSUMPTION_CONDITIONAL"],
        "distribution": "INDEPENDENT_UNIFORM_WHOLE_CURVE_OFFSETS",
        "output": key, "unit": "1", "samples": samples,
        "mean": statistics.fmean(values), "sample_standard_deviation": statistics.stdev(values),
        "percentiles": {"p2_5": quantile(.025), "p50": quantile(.5), "p97_5": quantile(.975)},
        "interval_meaning": "Central 95% of sampled synthetic model outputs; not a confidence interval or failure probability",
        "analytical_check": {"mean": baseline[key],
                             "variance": dt**2 * (widths[0]**2 + widths[1]**2) / 3},
        "support_bounds": {"min": min(c[key] for c in corners), "max": max(c[key] for c in corners)},
        "fracture_probability": {"status": "UNAVAILABLE", "value": None,
                                 "reason": "No bonded stress, strength, defect or calibrated failure model"},
        "limitations": ["Input distributions are assumptions, not measured uncertainty",
                        "No between-material correlation is supported",
                        "Numerical and model-form uncertainty are not quantified",
                        "Not coupled to the experimental 3D FEM model"],
    }
