"""Strict paired specimen-temperature comparison, not a firing predictor.

No interpolation, calibration, probability, or automatic validation approval.
All references identify immutable records resolved by the caller.
"""
from copy import deepcopy
import hashlib
import json
import math
from research.process.outcomes import OutcomeInputError, num

VERSION = 'paired-temperature-validation/0.1.0'
CONTEXT = {'body_revision', 'glaze_revision', 'application_revision',
           'firing_run_id', 'specimen_id', 'sensor_location'}


def validate_temperature_record(record, kind):
    """Validate one existing temperature-record contract without calculating metrics."""
    required = {'context', 'source_ref', 'evidence_kind', 'data_kind',
                'temperature_basis', 'unit', 'samples', 'method_version'}
    if not isinstance(record, dict) or set(record) != required:
        raise OutcomeInputError('INVALID_COMPARISON_FIELDS')
    if kind not in ('PREDICTED', 'OBSERVED') or record['evidence_kind'] != kind or record['unit'] != 'degC':
        raise OutcomeInputError('INCOMPATIBLE_QUANTITY')
    if record['temperature_basis'] != 'SPECIMEN':
        raise OutcomeInputError('SPECIMEN_TEMPERATURE_REQUIRED')
    if record['data_kind'] not in ('REAL', 'SYNTHETIC'):
        raise OutcomeInputError('INVALID_DATA_KIND')
    context = record['context']
    if not isinstance(context, dict) or set(context) != CONTEXT:
        raise OutcomeInputError('MISSING_SYSTEM_CONTEXT')
    for value in [*context.values(), record['source_ref'], record['method_version']]:
        if not isinstance(value, str) or not value.strip():
            raise OutcomeInputError('MISSING_PROVENANCE')
    if not isinstance(record['samples'], list) or not 1 <= len(record['samples']) <= 10001:
        raise OutcomeInputError('INVALID_SAMPLES')
    previous = -1
    for row in record['samples']:
        if not isinstance(row, dict) or set(row) != {'time_s', 'temperature_c'}:
            raise OutcomeInputError('INVALID_SAMPLE_FIELDS')
        time = num(row, 'time_s', 0, 1e8)
        num(row, 'temperature_c', -273.15, 2000)
        if time <= previous:
            raise OutcomeInputError('TIME_MUST_INCREASE')
        previous = time


def compare_temperature(prediction, observation):
    """Compare identical timestamps and context, retaining both input snapshots."""
    validate_temperature_record(prediction, 'PREDICTED')
    validate_temperature_record(observation, 'OBSERVED')
    if prediction['context'] != observation['context']:
        raise OutcomeInputError('SYSTEM_OR_SENSOR_MISMATCH')
    if prediction['data_kind'] != observation['data_kind']:
        raise OutcomeInputError('REAL_SYNTHETIC_MISMATCH')
    p, o = prediction['samples'], observation['samples']
    if [r['time_s'] for r in p] != [r['time_s'] for r in o]:
        raise OutcomeInputError('TIME_ALIGNMENT_REQUIRED')
    errors = [float(a['temperature_c']) - float(b['temperature_c']) for a,b in zip(p,o)]
    snapshot = deepcopy({'prediction': prediction, 'observation': observation})
    encoded = json.dumps({'version': VERSION, 'inputs': snapshot}, sort_keys=True, allow_nan=False).encode()
    return dict(status='AVAILABLE', evidence_kind='CALCULATED', method_version=VERSION,
                qualifier='SYNTHETIC_CHECK' if prediction['data_kind']=='SYNTHETIC' else 'PAIRED_COMPARISON_NOT_VALIDATION_APPROVAL',
                metrics={'bias_C': math.fsum(errors)/len(errors),
                         'mae_C': math.fsum(abs(e) for e in errors)/len(errors),
                         'rmse_C': math.sqrt(math.fsum(e*e for e in errors)/len(errors)),
                         'max_absolute_error_C': max(abs(e) for e in errors)},
                point_count=len(errors), independent_specimen_count=1,
                residuals_C=errors, uncertainty=None, acceptance_status='NOT_ASSESSED',
                input_snapshot=snapshot, input_hash=hashlib.sha256(encoded).hexdigest(),
                limitations=['Positive residual means prediction is hotter than measurement.',
                             'Unweighted point metrics; no time interpolation or duration weighting.',
                             'Samples from one specimen are not independent experiments.',
                             'Caller must verify source identity, sensor calibration and held-out status.',
                             'No fit on these observations and no claim of generalization.'])
