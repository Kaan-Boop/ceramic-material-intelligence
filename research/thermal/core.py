"""Pure small-strain thermal calculations. See docs/PHYSICS_RESEARCH.md.

CTE is the tangent coefficient for the SMALL_STRAIN approximation, in 1/K.
Mean/secant CTE and measured total dilatation are different input types.
"""

from dataclasses import dataclass, replace
from math import isfinite

MODEL_VERSION = "free-strain-piecewise-linear/0.1.0"
MAX_ABS_STRAIN = 0.01  # Conservative software scope limit, not a failure threshold.


class ModelInputError(ValueError):
    def __init__(self, code: str, field: str):
        self.code, self.field = code, field
        super().__init__(f"{code}: {field}")


def finite(value: float, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelInputError("FINITE_NUMBER_REQUIRED", field)
    try:
        result = float(value)
    except OverflowError:
        raise ModelInputError("FINITE_NUMBER_REQUIRED", field) from None
    if not isfinite(result):
        raise ModelInputError("FINITE_NUMBER_REQUIRED", field)
    return result


def temperature(value: float, field: str) -> float:
    value = finite(value, field)
    if value < -273.15:
        raise ModelInputError("BELOW_ABSOLUTE_ZERO", field)
    return value


@dataclass(frozen=True)
class Curve:
    material_id: str
    source_ref: str
    data_kind: str
    points: tuple[tuple[float, float], ...]
    coefficient_kind: str = "TANGENT_SMALL_STRAIN"
    unit: str = "1/K"

    def __post_init__(self):
        for field in ("material_id", "source_ref"):
            if not isinstance(getattr(self, field), str) or not getattr(self, field).strip():
                raise ModelInputError("PROVENANCE_REQUIRED", field)
        if self.data_kind not in ("SYNTHETIC", "MEASURED", "REPORTED"):
            raise ModelInputError("DATA_KIND_REQUIRED", "data_kind")
        if self.coefficient_kind != "TANGENT_SMALL_STRAIN" or self.unit != "1/K":
            raise ModelInputError("UNSUPPORTED_CTE_CONVENTION", "curve")
        if not isinstance(self.points, tuple) or len(self.points) < 2:
            raise ModelInputError("TWO_OR_MORE_POINTS_REQUIRED", "points")
        previous = None
        for point in self.points:
            if not isinstance(point, tuple) or len(point) != 2:
                raise ModelInputError("INVALID_POINT", "points")
            t = temperature(point[0], "points.temperature_c")
            finite(point[1], "points.alpha_per_k")
            if previous is not None and t <= previous:
                raise ModelInputError("STRICTLY_INCREASING_REQUIRED", "points")
            previous = t

    def at(self, t: float) -> float:
        t = temperature(t, "temperature_c")
        if not self.points[0][0] <= t <= self.points[-1][0]:
            raise ModelInputError("OUTSIDE_MEASURED_OR_ASSUMED_RANGE", self.material_id)
        for (a, x), (b, y) in zip(self.points, self.points[1:]):
            if a <= t <= b:
                return finite(x + (y - x) * ((t - a) / (b - a)), "interpolated_alpha")
        raise AssertionError("Validated interpolation interval missing")

    def shifted(self, offset: float) -> "Curve":
        offset = finite(offset, "alpha_offset_per_k")
        return replace(self, points=tuple((t, alpha + offset) for t, alpha in self.points))


def free_strain(curve: Curve, reference_c: float, target_c: float) -> float:
    """Signed integral alpha(T)dT; exact for the declared linear interpolant."""
    curve.at(reference_c)
    curve.at(target_c)
    lo, hi = sorted((reference_c, target_c))
    knots = [lo] + [t for t, _ in curve.points if lo < t < hi] + [hi]
    total = 0.0
    for a, b in zip(knots, knots[1:]):
        total += (b - a) * (curve.at(a) + curve.at(b)) / 2.0
        if not isfinite(total) or abs(total) > MAX_ABS_STRAIN:
            raise ModelInputError("SMALL_STRAIN_SCOPE_EXCEEDED", curve.material_id)
    return total if target_c >= reference_c else -total


@dataclass(frozen=True)
class Scenario:
    glaze: Curve
    body: Curve
    reference_temperature_c: float
    target_temperature_c: float
    reference_length_mm: float

    def __post_init__(self):
        temperature(self.reference_temperature_c, "reference_temperature_c")
        temperature(self.target_temperature_c, "target_temperature_c")
        if finite(self.reference_length_mm, "reference_length_mm") <= 0:
            raise ModelInputError("POSITIVE_LENGTH_REQUIRED", "reference_length_mm")


def calculate(scenario: Scenario) -> dict:
    g = free_strain(scenario.glaze, scenario.reference_temperature_c, scenario.target_temperature_c)
    b = free_strain(scenario.body, scenario.reference_temperature_c, scenario.target_temperature_c)
    length = scenario.reference_length_mm
    return {
        "glaze_free_strain": g,
        "body_free_strain": b,
        "mismatch_strain_glaze_minus_body": g - b,
        "glaze_length_change_mm": finite(length * g, "glaze_length_change_mm"),
        "body_length_change_mm": finite(length * b, "body_length_change_mm"),
        "free_length_difference_mm": finite(length * (g - b), "free_length_difference_mm"),
    }


def sensitivity(scenario: Scenario, steps: dict[str, float]) -> list[dict]:
    """Explicit one-at-a-time scenarios, NOT probability/confidence intervals."""
    allowed = {"glaze_alpha_offset_per_k", "body_alpha_offset_per_k",
               "reference_temperature_c", "target_temperature_c", "reference_length_mm"}
    if not isinstance(steps, dict) or set(steps) - allowed:
        raise ModelInputError("UNKNOWN_SENSITIVITY_PARAMETER", "sensitivity_steps")
    baseline = calculate(scenario)
    rows = []
    for parameter, step in sorted(steps.items()):
        if finite(step, parameter) <= 0:
            raise ModelInputError("POSITIVE_STEP_REQUIRED", parameter)
        for sign in (-1, 1):
            delta = sign * step
            if parameter.endswith("alpha_offset_per_k"):
                field = "glaze" if parameter.startswith("glaze") else "body"
                changed = replace(scenario, **{field: getattr(scenario, field).shifted(delta)})
            else:
                changed = replace(scenario, **{parameter: getattr(scenario, parameter) + delta})
            result = calculate(changed)
            rows.append({"parameter": parameter, "input_delta": delta,
                         "mismatch_strain": result["mismatch_strain_glaze_minus_body"],
                         "change_from_baseline_strain": result["mismatch_strain_glaze_minus_body"]
                         - baseline["mismatch_strain_glaze_minus_body"],
                         "free_length_difference_mm": result["free_length_difference_mm"]})
    return rows
