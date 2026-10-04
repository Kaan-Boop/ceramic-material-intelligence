"""Generic, material-agnostic simulation scenario contract.

This module only validates and fingerprints a scenario. It does not infer fired
surface, fit or defect probabilities. Physical models consume this contract in
later stages and must report their own scope and evidence status.
"""
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from typing import Literal


MaterialRole = Literal["BODY", "ENGOBE", "GLAZE", "ADDITION", "OVERGLAZE"]
ApplicationMethod = Literal["NONE", "DIP", "BRUSH", "SPRAY", "POUR", "SCREEN", "OTHER"]

_MATERIAL_ROLES = {"BODY", "ENGOBE", "GLAZE", "ADDITION", "OVERGLAZE"}
_APPLICATION_METHODS = {"NONE", "DIP", "BRUSH", "SPRAY", "POUR", "SCREEN", "OTHER"}
_GEOMETRY_KINDS = {"TILE", "PLATE", "CYLINDER", "SPHERE", "CUSTOM"}


def _finite_nonnegative(value: float, field_name: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be a finite non-negative number")


@dataclass(frozen=True)
class MaterialRef:
    analysis_id: str
    role: MaterialRole
    amount_g: float | None = None
    layer_id: str | None = None

    def __post_init__(self):
        if not self.analysis_id.strip():
            raise ValueError("analysis_id is required")
        if self.role not in _MATERIAL_ROLES:
            raise ValueError("unsupported material role")
        if self.amount_g is not None:
            if not isinstance(self.amount_g, (int, float)) or isinstance(self.amount_g, bool) or not math.isfinite(self.amount_g) or self.amount_g <= 0:
                raise ValueError("amount_g must be a finite positive number when supplied")


@dataclass(frozen=True)
class LayerSpec:
    layer_id: str
    materials: tuple[MaterialRef, ...]
    application_method: ApplicationMethod = "NONE"
    coat_count: int = 0
    dry_thickness_um: float | None = None
    wet_thickness_um: float | None = None
    drying_minutes: float | None = None

    def __post_init__(self):
        if not self.layer_id.strip() or not self.materials:
            raise ValueError("layer_id and at least one material are required")
        if self.application_method not in _APPLICATION_METHODS:
            raise ValueError("unsupported application method")
        if self.coat_count < 0:
            raise ValueError("coat_count cannot be negative")
        for name in ("dry_thickness_um", "wet_thickness_um", "drying_minutes"):
            value = getattr(self, name)
            if value is not None:
                _finite_nonnegative(value, name)


@dataclass(frozen=True)
class FiringSegment:
    target_c: float
    rate_c_per_hour: float | None = None
    hold_minutes: float = 0.0

    def __post_init__(self):
        if not isinstance(self.target_c, (int, float)) or isinstance(self.target_c, bool) or not math.isfinite(self.target_c) or not 0 <= self.target_c <= 1800:
            raise ValueError("target_c must be within 0–1800 °C")
        if self.rate_c_per_hour is not None and (not isinstance(self.rate_c_per_hour, (int, float)) or isinstance(self.rate_c_per_hour, bool) or not math.isfinite(self.rate_c_per_hour) or self.rate_c_per_hour <= 0):
            raise ValueError("rate_c_per_hour must be a finite positive number when supplied")
        _finite_nonnegative(self.hold_minutes, "hold_minutes")


@dataclass(frozen=True)
class FiringSchedule:
    name: str
    start_c: float
    segments: tuple[FiringSegment, ...]
    atmosphere: str = "UNKNOWN"

    def __post_init__(self):
        if not self.name.strip() or not self.segments:
            raise ValueError("firing schedule name and segments are required")
        if not isinstance(self.start_c, (int, float)) or isinstance(self.start_c, bool) or not math.isfinite(self.start_c) or not 0 <= self.start_c <= 1800:
            raise ValueError("start_c must be within 0–1800 °C")


@dataclass(frozen=True)
class GeometrySpec:
    kind: Literal["TILE", "PLATE", "CYLINDER", "SPHERE", "CUSTOM"]
    thickness_mm: float
    length_mm: float | None = None
    width_mm: float | None = None
    diameter_mm: float | None = None

    def __post_init__(self):
        if self.kind not in _GEOMETRY_KINDS:
            raise ValueError("unsupported geometry kind")
        if not isinstance(self.thickness_mm, (int, float)) or isinstance(self.thickness_mm, bool) or not math.isfinite(self.thickness_mm) or self.thickness_mm <= 0:
            raise ValueError("thickness_mm must be a finite positive number")
        for name in ("length_mm", "width_mm", "diameter_mm"):
            value = getattr(self, name)
            if value is not None:
                _finite_nonnegative(value, name)


@dataclass(frozen=True)
class SimulationTarget:
    objective: str
    requested_outputs: tuple[str, ...] = ()
    reference_temperature_c: float | None = None

    def __post_init__(self):
        if not self.objective.strip():
            raise ValueError("objective is required")
        if self.reference_temperature_c is not None:
            if not isinstance(self.reference_temperature_c, (int, float)) or isinstance(self.reference_temperature_c, bool) or not math.isfinite(self.reference_temperature_c):
                raise ValueError("reference_temperature_c must be finite when supplied")


@dataclass(frozen=True)
class SimulationScenario:
    scenario_id: str
    body: LayerSpec
    layers: tuple[LayerSpec, ...]
    bisque: FiringSchedule | None
    final_firing: FiringSchedule
    geometry: GeometrySpec
    target: SimulationTarget
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.scenario_id.strip():
            raise ValueError("scenario_id is required")
        if self.body.layer_id != "body":
            raise ValueError("body layer_id must be 'body'")
        ids = [self.body.layer_id, *(layer.layer_id for layer in self.layers)]
        if len(ids) != len(set(ids)):
            raise ValueError("layer_id values must be unique")
        if any(layer.layer_id == "body" for layer in self.layers):
            raise ValueError("body must be supplied separately")

    def snapshot(self) -> dict:
        return asdict(self)

    def input_hash(self) -> str:
        payload = json.dumps(self.snapshot(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
