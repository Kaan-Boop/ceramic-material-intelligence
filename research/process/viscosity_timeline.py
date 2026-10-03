"""Sampled reference-property evaluation; not a thermal or flow integrator."""
from copy import deepcopy
import hashlib
import json
from research.process.outcomes import num, OutcomeInputError
from research.process.reference_viscosity import viscosity, MATERIAL_ID, VERSION as PROPERTY_VERSION

VERSION = 'reference-viscosity-timeline/0.1.0'


def evaluate(*, material_id, samples, temperature_basis, source_ref):
    if material_id != MATERIAL_ID:
        raise OutcomeInputError('REFERENCE_MATERIAL_MISMATCH')
    if temperature_basis not in ('MEASURED_SPECIMEN', 'MODELED_SPECIMEN', 'PROGRAMMED_KILN', 'SYNTHETIC'):
        raise OutcomeInputError('INVALID_TEMPERATURE_BASIS')
    if not isinstance(source_ref, str) or not source_ref.strip():
        raise OutcomeInputError('MISSING_TEMPERATURE_SOURCE')
    if not isinstance(samples, list) or not 1 <= len(samples) <= 10001:
        raise OutcomeInputError('INVALID_TIME_SERIES')
    snapshot = deepcopy(samples)
    rows = []
    previous = -1.0
    for sample in snapshot:
        if not isinstance(sample, dict) or set(sample) != {'time_s', 'temperature_c'}:
            raise OutcomeInputError('INVALID_SAMPLE_FIELDS')
        time = num(sample, 'time_s', 0, 1e8)
        t = num(sample, 'temperature_c', -273.15, 1800)
        if time <= previous:
            raise OutcomeInputError('TIME_MUST_INCREASE')
        previous = time
        row = dict(time_s=time, temperature_c=t, viscosity_pa_s=None)
        if temperature_basis == 'PROGRAMMED_KILN':
            row.update(status='UNAVAILABLE', reason='SPECIMEN_TEMPERATURE_REQUIRED')
        elif not 821.5 <= t <= 1434.3:
            row.update(status='UNAVAILABLE', reason='OUTSIDE_REFERENCE_PROPERTY_SCOPE')
        else:
            row.update(status='AVAILABLE', reason=None,
                       viscosity_pa_s=viscosity(t, material_id)['viscosity_pa_s'])
        rows.append(row)
    available = sum(row['status'] == 'AVAILABLE' for row in rows)
    inputs = dict(material_id=material_id, samples=snapshot,
                  temperature_basis=temperature_basis, source_ref=source_ref)
    encoded = json.dumps(dict(inputs=inputs, version=VERSION, property_version=PROPERTY_VERSION),
                         sort_keys=True, allow_nan=False).encode()
    return dict(status='AVAILABLE' if available == len(rows) else 'PARTIAL' if available else 'UNAVAILABLE',
                method_version=VERSION, property_version=PROPERTY_VERSION,
                evidence_kind='PREDICTED', method_kind='EMPIRICAL',
                qualifier='SYNTHETIC_SCENARIO' if temperature_basis == 'SYNTHETIC' else 'REFERENCE_PROPERTY_EVALUATION',
                input_snapshot=inputs, input_hash=hashlib.sha256(encoded).hexdigest(), series=rows,
                available_sample_count=available, sample_count=len(rows), uncertainty=None,
                physical_validation='NOT_PERFORMED_BY_PROJECT',
                limitations=['Evaluates provided sample temperatures, does not solve heat transfer.',
                             'Unavailable intervals are not zero viscosity or zero flow.',
                             'No interpolation between samples, time integration or cumulative flow.',
                             'Coverage count is not time coverage, probability or confidence.',
                             'Historical NBS 710 fit only; not a general glaze model.'])
