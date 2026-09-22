"""Study-scoped reported MTGA summaries, NOT a time series or kinetic model."""
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

TABLE = 'materials-17-02231-t002'
VERSION = 'moisture-table/0.1.0'
EXPECTED = ['Na_Montmorillonite', 'Na_Montmorillonite (Rec)', 'Ca-Montmorillonite',
            'Ca-Montmorillonite (Rec)', 'Palygorskite', 'Palygorskite (Rec)',
            'Stevensite', 'Stevensite (Rec)', 'Sepiolite', 'Sepiolite (Rec)']


def text(element):
    return ' '.join(''.join(element.itertext()).split())


def reported_number(raw, unit, maximum):
    if raw == '-':
        return dict(value=None, raw=raw, unit=unit, status='UNAVAILABLE', missing_reason='REPORTED_DASH')
    value = float(raw)
    if not math.isfinite(value) or not 0 <= value <= maximum:
        raise ValueError('INVALID_REPORTED_VALUE')
    return dict(value=value, raw=raw, unit=unit, status='AVAILABLE', uncertainty=None)


def normalize(raw, source):
    root = ET.fromstring(raw)
    matches = root.findall(f".//table-wrap[@id='{TABLE}']")
    if len(matches) != 1:
        raise ValueError('EXACT_REVIEWED_TABLE_REQUIRED')
    table = matches[0]
    headers = [text(c) for c in table.findall('./table/thead/tr/th')]
    if len(headers) != 7 or headers[:5] != ['Sample', 'T (°C)', 'I Loss (%)', 'T (°C)', 'II Loss (%)']:
        raise ValueError('TABLE_SCHEMA_CHANGED')
    rows = table.findall('./table/tbody/tr')
    if len(rows) != 10:
        raise ValueError('EXPECTED_TEN_REPORTED_SAMPLE_STATES')
    results = []
    for index, row in enumerate(rows):
        cells = [text(c) for c in row.findall('td')]
        if len(cells) != (7 if index % 2 == 0 else 6) or cells[0] != EXPECTED[index]:
            raise ValueError('ROW_LAYOUT_OR_SAMPLE_ID_CHANGED')
        events = []
        for stage, offset in [('I', 1), ('II', 3)]:
            events.append(dict(stage=stage, evidence_kind='OBSERVED', qualifier='REPORTED_STUDY_SUMMARY',
                               reported_temperature=reported_number(cells[offset], 'degC', 260),
                               mass_loss=reported_number(cells[offset+1], 'wt_percent', 100),
                               temperature_semantics='AS_REPORTED_IN_TABLE_NOT_UNIVERSAL_ONSET'))
        if sum(e['mass_loss']['value'] for e in events) > 100:
            raise ValueError('LOSS_SUM_OVER_100')
        results.append(dict(id=f'PMC11123035-table2-row{index+1}', sample_label=cells[0],
                            condition='RECONDITIONED' if '(Rec)' in cells[0] else 'CONDITIONED',
                            events=events,
                            activation_energy=dict(**reported_number(cells[5], 'kJ_per_mol', 1000),
                                                   evidence_kind='PREDICTED', method_kind='EMPIRICAL',
                                                   qualifier='REPORTED_MTGA_DERIVATION_NOT_UNIVERSAL_KINETICS'),
                            original_cells=cells, source=source, source_table_id=TABLE,
                            source_row_1based=index+1, status='STUDY_REFERENCE_ONLY',
                            time_series_status='UNAVAILABLE', vapor_source_status='UNAVAILABLE',
                            limitation='No timestamps, absolute sample mass or calibrated species flow in this table'))
    return dict(schema_version=VERSION, source_sha256=hashlib.sha256(raw).hexdigest(),
                records=results, record_count=len(results), distinct_mineral_groups=5,
                missing_event_temperatures=sum(e['reported_temperature']['value'] is None for r in results for e in r['events']),
                kinetic_models_fitted=0, core_material_analyses_added=0,
                protocol=dict(relative_humidity_percent=75, conditioning_hours=48,
                              reconditioning_prior_drying_c=150, reconditioning_prior_drying_hours=24,
                              atmosphere='N2', sample_flow_cm3_min=60, balance_flow_cm3_min=40,
                              temperature_range_c=[25,260],
                              program='MTGA; full modulation details require source review; not a constant-rate TGA trace'),
                excluded_column='Delta E spans paired rows; original cell text retained, not independently counted',
                limitations=['Ten sample states are not ten independent mineral populations',
                             'Reported observations are not a validated calibration set for our engine'])


def main():
    m = json.loads(Path('data/manifests/physics-pool-2026-09-22.json').read_text(encoding='utf-8'))
    source = next(s for s in m['sources'] if s['source_id'] == 'PMC11123035')
    entry = next(e for e in m['files'] if e['source_id'] == 'PMC11123035')
    raw = (Path('storage/physics-pool/2026-09-22') / entry['raw_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError('RAW_HASH_MISMATCH')
    result = normalize(raw, source)
    target = Path('data/reference/moisture-study-observations-v1.json')
    with target.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','protocol','limitations')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
