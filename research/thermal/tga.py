"""Signed TGA interval accounting and guarded isothermal vapor replay.

No smoothing, kinetic fitting, species inference or sample-to-kiln scaling.
"""
from copy import deepcopy
import math
from research.chemistry.foundation import digest
from .vapor import chamber_segment

VERSION = 'tga-accounting/0.1.0'


def number(value, name, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or not minimum <= value <= 1e9:
        raise ValueError('INVALID_NUMBER: ' + name)
    return value


def analyze_trace(trace):
    """Input samples are [elapsed seconds, sample temperature Celsius, mass mg]."""
    if not isinstance(trace, dict):
        raise ValueError('TRACE_OBJECT_REQUIRED')
    for key in ('source_ref', 'sample_id', 'atmosphere', 'mass_basis'):
        if not isinstance(trace.get(key), str) or not trace[key].strip():
            raise ValueError('TRACE_METADATA_REQUIRED: ' + key)
    if trace['mass_basis'] != 'ABSOLUTE_SAMPLE_MASS_MG':
        raise ValueError('ABSOLUTE_MASS_REQUIRED_NO_PERCENT_BASE_INFERENCE')
    if trace.get('data_kind') not in ('MEASURED', 'SYNTHETIC'):
        raise ValueError('EXPLICIT_DATA_KIND_REQUIRED')
    samples = trace.get('samples')
    if not isinstance(samples, list) or not 2 <= len(samples) <= 100000:
        raise ValueError('TRACE_REQUIRES_2_TO_100000_SAMPLES')
    previous = None
    for point in samples:
        if not isinstance(point, (list, tuple)) or len(point) != 3:
            raise ValueError('SAMPLE_REQUIRES_TIME_S_TEMPERATURE_C_MASS_MG')
        t, temperature, mass = point
        number(t, 'time_s')
        number(temperature, 'temperature_c', -273.15)
        number(mass, 'mass_mg')
        if temperature <= -273.15 or (previous is not None and t <= previous):
            raise ValueError('INVALID_TEMPERATURE_OR_NONINCREASING_TIME')
        previous = t
    if samples[0][2] <= 0:
        raise ValueError('POSITIVE_INITIAL_MASS_REQUIRED')
    intervals = []
    for i, (a, b) in enumerate(zip(samples, samples[1:])):
        loss_kg = (a[2] - b[2]) * 1e-6
        intervals.append(dict(index=i, start_s=a[0], end_s=b[0], duration_s=b[0]-a[0],
                              signed_net_loss_kg=loss_kg,
                              interval_average_net_loss_kg_s=loss_kg/(b[0]-a[0]),
                              source_temperatures_c=[a[1], b[1]],
                              gas_identity='UNKNOWN', gas_source_status='UNAVAILABLE'))
    snapshot = deepcopy(trace)
    return dict(engine_version=VERSION, input_snapshot=snapshot,
                input_hash=digest({'trace': snapshot, 'version': VERSION}),
                evidence_kind='CALCULATED', method_kind='DETERMINISTIC',
                qualifier='DERIVED_FROM_' + trace['data_kind'], intervals=intervals,
                net_mass_loss_kg=(samples[0][2]-samples[-1][2])*1e-6,
                positive_loss_kg=math.fsum(max(0, i['signed_net_loss_kg']) for i in intervals),
                mass_gain_kg=math.fsum(max(0, -i['signed_net_loss_kg']) for i in intervals),
                uncertainty=None,
                warnings=['Net loss does not identify or quantify individual gases',
                          'Average interval slope is not an instantaneous DTG peak',
                          'Mass gain and noise are preserved; no smoothing or clipping'])


def replay_water(trace, allocations, chamber):
    """Explicit interval H2O allocations; chamber is a separate fixed-T scenario.

    allocations: one {water_fraction, kind, source_ref} per interval. Fraction
    refers to net lost mass, not MS signal intensity. No sample mass scaling.
    """
    report = analyze_trace(trace)
    if not isinstance(allocations, list) or len(allocations) != len(report['intervals']):
        raise ValueError('ONE_WATER_ALLOCATION_PER_INTERVAL_REQUIRED')
    if not isinstance(chamber, dict):
        raise ValueError('CHAMBER_OBJECT_REQUIRED')
    required = {'volume_m3', 'flow_m3_s', 'initial_kg_m3', 'inlet_kg_m3',
                'saturation_kg_m3', 'temperature_c', 'source_ref'}
    if set(chamber) != required:
        raise ValueError('EXPLICIT_FIXED_CHAMBER_FIELDS_REQUIRED')
    number(chamber['temperature_c'], 'chamber_temperature_c', -273.15)
    if chamber['temperature_c'] <= -273.15:
        raise ValueError('INVALID_CHAMBER_TEMPERATURE')
    for interval, allocation in zip(report['intervals'], allocations):
        if not isinstance(allocation, dict):
            raise ValueError('ALLOCATION_OBJECT_REQUIRED')
        fraction = number(allocation.get('water_fraction'), 'water_fraction')
        if fraction > 1 or allocation.get('kind') not in ('QUANTITATIVE_ALLOCATION', 'SCENARIO_ASSUMPTION'):
            raise ValueError('QUANTITATIVE_OR_SCENARIO_ALLOCATION_REQUIRED')
        if not isinstance(allocation.get('source_ref'), str) or not allocation['source_ref'].strip():
            raise ValueError('ALLOCATION_SOURCE_REQUIRED')
        if interval['signed_net_loss_kg'] < 0:
            raise ValueError('MASS_GAIN_REQUIRES_SEPARATE_REACTION_MODEL')
    inputs = deepcopy(dict(trace=trace, allocations=allocations, chamber=chamber))
    concentration = chamber['initial_kg_m3']
    results = []
    for interval, allocation in zip(report['intervals'], allocations):
        kwargs = {k: chamber[k] for k in required - {'temperature_c', 'initial_kg_m3'}}
        result = chamber_segment(**kwargs, initial_kg_m3=concentration,
                                 duration_s=interval['duration_s'],
                                 source_kg_s=interval['interval_average_net_loss_kg_s']*allocation['water_fraction'])
        results.append(dict(interval_index=interval['index'], water_allocation=deepcopy(allocation), result=result))
        if result['status'] != 'AVAILABLE':
            break
        concentration = result['final_vapor_kg_m3']
    available = results[-1]['result']['status'] == 'AVAILABLE'
    return dict(engine_version=VERSION, input_snapshot=inputs,
                input_hash=digest({'inputs': inputs, 'version': VERSION,
                                   'vapor_version': results[0]['result']['engine_version']}),
                trace_report=report, segments=results, status='AVAILABLE' if available else 'UNAVAILABLE',
                unprocessed_intervals=len(allocations)-len(results),
                final_vapor_kg_m3=concentration if available else None,
                evidence_kind='PREDICTED', method_kind='DETERMINISTIC', qualifier='IDEALIZED_REPLAY',
                warnings=['A replay of supplied release history, not a new heating schedule prediction',
                          'Sample temperature is metadata; chamber temperature is independently prescribed',
                          'No latent heat, condensation, sample scaling or gas transport delay model',
                          'Quantitative allocation is a caller declaration, not an instrument calibration check'])
