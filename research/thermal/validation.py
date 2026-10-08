"""Run the inert-slab solver and compare a declared specimen sensor trace.

No fitted parameters, time shifts, real/synthetic mixing or validation approval.
The original observations and thermal solver remain unchanged.
"""
from bisect import bisect_left
from copy import deepcopy
import hashlib
import json

from research.process.outcomes import OutcomeInputError, num
from research.process.validation import CONTEXT, compare_temperature, validate_temperature_record
from research.thermal.kiln_1d import simulate

VERSION = "kiln-thermal-comparison/0.1.0"


class ThermalComparisonError(ValueError):
    pass


def _fields(value, names, path):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ThermalComparisonError("INVALID_FIELDS:" + path)


def _text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 500:
        raise ThermalComparisonError("MISSING_OR_INVALID_REFERENCE")


def _probe(probe):
    if not isinstance(probe, dict):
        raise ThermalComparisonError("INVALID_PROBE")
    kind = probe.get("kind")
    if kind in ("LEFT_SURFACE", "RIGHT_SURFACE"):
        _fields(probe, "kind", "probe")
    elif kind == "LAYER_MIDPOINT":
        _fields(probe, "kind layer_id", "probe")
        _text(probe["layer_id"])
    else:
        raise ThermalComparisonError("UNSUPPORTED_SPECIMEN_PROBE")


def _prepare(request):
    _fields(request, "schema_version case context probe time_origin_ref alignment observation", "request")
    if request["schema_version"] != "kiln-thermal-comparison-request-v1":
        raise ThermalComparisonError("UNSUPPORTED_SCHEMA")
    context = request["context"]
    if not isinstance(context, dict) or set(context) != CONTEXT:
        raise ThermalComparisonError("MISSING_SYSTEM_CONTEXT")
    for value in context.values():
        _text(value)
    _text(request["time_origin_ref"])
    _probe(request["probe"])
    observation = request["observation"]
    _fields(observation, "record probe time_origin_ref sensor dataset_role", "observation")
    validate_temperature_record(observation["record"], "OBSERVED")
    _probe(observation["probe"])
    if observation["probe"] != request["probe"]:
        raise ThermalComparisonError("SENSOR_PROBE_MISMATCH")
    if observation["record"]["context"] != context:
        raise ThermalComparisonError("SYSTEM_OR_SENSOR_MISMATCH")
    if observation["time_origin_ref"] != request["time_origin_ref"]:
        raise ThermalComparisonError("TIME_ORIGIN_MISMATCH")
    if observation["dataset_role"] not in ("CALIBRATION", "HELD_OUT", "UNSPECIFIED"):
        raise ThermalComparisonError("INVALID_DATASET_ROLE")
    sensor = observation["sensor"]
    _fields(sensor, "sensor_id method calibration_ref standard_uncertainty_c", "sensor")
    _text(sensor["sensor_id"])
    _text(sensor["method"])
    if sensor["calibration_ref"] is not None:
        _text(sensor["calibration_ref"])
    if sensor["standard_uncertainty_c"] is not None:
        num(sensor, "standard_uncertainty_c", 0, 1000)
    alignment = request["alignment"]
    if not isinstance(alignment, dict):
        raise ThermalComparisonError("INVALID_ALIGNMENT")
    if alignment.get("method") == "EXACT":
        _fields(alignment, "method", "alignment")
    elif alignment.get("method") == "LINEAR":
        _fields(alignment, "method max_interval_s", "alignment")
        num(alignment, "max_interval_s", 1e-6, 3600)
    else:
        raise ThermalComparisonError("EXPLICIT_ALIGNMENT_REQUIRED")


def _probe_values(thermal, probe):
    if probe["kind"] == "LAYER_MIDPOINT":
        layers = thermal["input_snapshot"]["layers"]
        index = next((i for i, layer in enumerate(layers) if layer["layer_id"] == probe["layer_id"]), None)
        if index is None:
            raise ThermalComparisonError("UNKNOWN_PROBE_LAYER")
        depth = sum(layer["thickness_m"] for layer in layers[:index]) + layers[index]["thickness_m"]/2
        return [row["layer_midpoint_c"][probe["layer_id"]] for row in thermal["series"]], depth
    key = "left_surface_c" if probe["kind"] == "LEFT_SURFACE" else "right_surface_c"
    depth = 0. if probe["kind"] == "LEFT_SURFACE" else sum(l["thickness_m"] for l in thermal["input_snapshot"]["layers"])
    return [row[key] for row in thermal["series"]], depth


def _sample(times, values, time, alignment):
    if time < times[0] or time > times[-1]:
        raise ThermalComparisonError("OBSERVATION_OUTSIDE_SIMULATION_TIME")
    right = bisect_left(times, time)
    if right < len(times) and time == times[right]:
        return values[right], {"method": "EXACT", "left_time_s": time, "right_time_s": time, "right_weight": 0.}
    if alignment["method"] != "LINEAR":
        raise ThermalComparisonError("EXACT_SAMPLE_TIME_REQUIRED")
    left = right - 1
    gap = times[right] - times[left]
    if gap > alignment["max_interval_s"]:
        raise ThermalComparisonError("INTERPOLATION_INTERVAL_TOO_LARGE")
    weight = (time-times[left])/gap
    value = (1-weight)*values[left] + weight*values[right]
    return value, {"method": "LINEAR", "left_time_s": times[left], "right_time_s": times[right], "right_weight": weight}


def evaluate(request):
    """Compute predictions server-side, align them explicitly, retain measurement lineage.

    REAL/HELD_OUT/calibration references are declarations, not independently
    authenticated evidence. No numerical threshold promotes a model to validated.
    """
    _prepare(request)
    thermal = simulate(request["case"])
    observation = request["observation"]
    data_kind = "SYNTHETIC" if thermal["contains_synthetic_inputs"] else "REAL"
    if observation["record"]["data_kind"] != data_kind:
        raise ThermalComparisonError("REAL_SYNTHETIC_MISMATCH")
    values, depth = _probe_values(thermal, request["probe"])
    times = [row["time_s"] for row in thermal["series"]]
    predicted_samples, pairs = [], []
    for sample in observation["record"]["samples"]:
        value, bracket = _sample(times, values, sample["time_s"], request["alignment"])
        predicted_samples.append({"time_s": sample["time_s"], "temperature_c": value})
        pairs.append({"time_s": sample["time_s"], "predicted_c": value, "observed_c": sample["temperature_c"],
                      "residual_c": value-sample["temperature_c"], "alignment": bracket})
    prediction = {"context": deepcopy(request["context"]), "source_ref": "thermal-input:" + thermal["input_hash"],
                  "evidence_kind": "PREDICTED", "data_kind": data_kind, "temperature_basis": "SPECIMEN", "unit": "degC",
                  "samples": predicted_samples, "method_version": thermal["engine_version"] + "+" + VERSION}
    comparison = compare_temperature(prediction, observation["record"])
    warnings = []
    if data_kind == "SYNTHETIC":
        warnings.append("SYNTHETIC_CHECK_NOT_EXPERIMENTAL_VALIDATION")
    if observation["sensor"]["calibration_ref"] is None:
        warnings.append("SENSOR_CALIBRATION_UNKNOWN")
    if observation["sensor"]["standard_uncertainty_c"] is None:
        warnings.append("SENSOR_UNCERTAINTY_UNKNOWN")
    if observation["dataset_role"] != "HELD_OUT":
        warnings.append("NOT_DECLARED_HELD_OUT")
    interpolated = sum(pair["alignment"]["method"] == "LINEAR" for pair in pairs)
    if interpolated:
        warnings.append("PREDICTIONS_TIME_INTERPOLATED")
    snapshot = deepcopy(request)
    input_hash = hashlib.sha256(json.dumps({"version": VERSION, "input": snapshot, "thermal_input_hash": thermal["input_hash"],
                                           "comparison_version": comparison["method_version"]},
                                          sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return {"schema_version": "kiln-thermal-comparison-report-v1", "method_version": VERSION,
            "evidence_kind": "CALCULATED", "method_kind": "DETERMINISTIC", "status": "AVAILABLE",
            "qualifier": comparison["qualifier"], "input_hash": input_hash, "input_snapshot": snapshot,
            "thermal_report": thermal, "comparison": comparison, "pairs": pairs,
            "probe_depth_m": depth, "time_interpolated_count": interpolated,
            "time_exact_count": len(pairs)-interpolated,
            "observed_real_specimen_count": 0 if data_kind == "SYNTHETIC" else 1,
            "dataset_role": observation["dataset_role"], "acceptance_status": "NOT_ASSESSED",
            "physical_validation": "NOT_ESTABLISHED", "uncertainty": None, "warnings": warnings,
            "limitations": ["An error report is not model validation approval; no acceptance limits are inferred.",
                            "Only predictions may be linearly interpolated in time, and only with explicit opt-in and interval limit.",
                            "No extrapolation, time shift, missing-sample removal, smoothing or sensor-response correction.",
                            "Sensor IDs, physical context, calibration and held-out status are caller declarations, not verified registry links.",
                            "A point probe is not an infrared area average or a kiln gas measurement.",
                            "Standard sensor uncertainty is retained but not combined into a model confidence interval.",
                            "Metrics weight samples equally; one trace is not many independent specimens.",
                            "No parameter fitting, chemistry coupling or phase/defect model is performed."]}
