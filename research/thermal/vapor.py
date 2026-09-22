"""Isothermal dilute-vapor control-volume benchmark, not a kiln controller.

V dc/dt = source + Q(c_in-c). Constant V,Q,T per segment. Perfect mixing,
equal volumetric inflow/outflow, negligible source volume, no condensation.
"""
import math
from research.chemistry.foundation import digest

VERSION = 'vapor-control-volume/0.1.0'


def chamber_segment(*, volume_m3, flow_m3_s, duration_s, initial_kg_m3,
                    inlet_kg_m3, source_kg_s, saturation_kg_m3, source_ref):
    values = dict(volume_m3=volume_m3, flow_m3_s=flow_m3_s, duration_s=duration_s,
                  initial_kg_m3=initial_kg_m3, inlet_kg_m3=inlet_kg_m3,
                  source_kg_s=source_kg_s, saturation_kg_m3=saturation_kg_m3)
    if not isinstance(source_ref, str) or not source_ref.strip():
        raise ValueError('SOURCE_OR_SCENARIO_REFERENCE_REQUIRED')
    for key, value in values.items():
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or value > 1e9:
            raise ValueError('INVALID_FINITE_NONNEGATIVE_INPUT: ' + key)
    if volume_m3 < 1e-9 or saturation_kg_m3 <= 0:
        raise ValueError('POSITIVE_VOLUME_AND_SATURATION_REQUIRED')
    if initial_kg_m3 > saturation_kg_m3 or inlet_kg_m3 > saturation_kg_m3:
        raise ValueError('SUPERSATURATED_INPUT_OUTSIDE_MODEL')
    x = flow_m3_s * duration_s / volume_m3
    # Stable analytical integration, including zero ventilation and small x.
    f = -math.expm1(-x) / x if x else 1.0
    g = (x / 2 - x*x / 6 + x*x*x / 24) if x < 1e-4 else 1 - f
    end = initial_kg_m3 + (inlet_kg_m3-initial_kg_m3)*(-math.expm1(-x)) + source_kg_s*duration_s/volume_m3*f
    initial = initial_kg_m3 * volume_m3
    supplied = source_kg_s * duration_s
    incoming = flow_m3_s * inlet_kg_m3 * duration_s
    outgoing = (flow_m3_s * duration_s * (inlet_kg_m3*g + initial_kg_m3*f)
                + supplied*g)
    residual = initial + supplied + incoming - outgoing - end*volume_m3
    available = end <= saturation_kg_m3
    return dict(engine_version=VERSION, input_snapshot={**values, 'source_ref': source_ref},
                input_hash=digest({**values, 'source_ref': source_ref, 'version': VERSION}),
                evidence_kind='PREDICTED', method_kind='DETERMINISTIC', qualifier='IDEALIZED_SCENARIO',
                status='AVAILABLE' if available else 'UNAVAILABLE',
                unavailable_reason=None if available else 'SATURATION_CROSSED_CONDENSATION_MODEL_REQUIRED',
                final_vapor_kg_m3=end if available else None,
                diagnostic_unconstrained_vapor_kg_m3=end,
                mass_balance_residual_kg=residual,
                diagnostic_mass_budget_kg=dict(initial=initial, source=supplied, inlet=incoming,
                                               outlet=outgoing, final_unconstrained=end*volume_m3),
                uncertainty=None, defect_probability=None,
                limitations=['Prescribed vapor source, not evaporation/dehydroxylation kinetics',
                             'Saturation concentration supplied for the same fixed temperature',
                             'Dilute perfect mixing; no pores, pressure, latent heat or spatial gradients',
                             'No validation against a real kiln; not a safety or firing-control tool'])
