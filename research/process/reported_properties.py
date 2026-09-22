"""Validate and compare reviewed factual notes; no chemistry or fit prediction.

Research-only caller: rights review is required before serving catalogue data.
All source assertions remain in the input snapshot, including disagreements.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from research.commercial_catalogue import canonical
from research.process.assessment import number, firing_window, ProcessInputError

VERSION = 'reported-properties/1.0.0'
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/research/turkey-body-properties-2026-09-23.json'


def validate_bundle(bundle, catalogue):
    ids = set()
    keys = {(canonical(r['brand']), canonical(r['product_code'] or r['source_name_verbatim']))
            for r in catalogue if r['entity_kind'] == 'CLAY_BODY'}
    for row in bundle['products']:
        if row['id'] in ids:
            raise ValueError('DUPLICATE_PROPERTY_PRODUCT')
        ids.add(row['id'])
        if (canonical(row['brand']), canonical(row['catalogue_key'])) not in keys:
            raise ValueError('ORPHAN_PROPERTY_PRODUCT')
        if not row['source_url'].startswith('https://') or not row['source_locator']:
            raise ValueError('MISSING_SOURCE')
        for window in row['firing_windows']:
            if window['stage'] not in ('GLAZE', 'BISQUE') or not window['locator']:
                raise ValueError('INVALID_WINDOW_METADATA')
            low, high = number(window['min_c'], 'min_c'), number(window['max_c'], 'max_c')
            if low > high:
                raise ValueError('INVERTED_WINDOW')
            if window.get('kind', 'RANGE') not in ('RANGE', 'POINT_TARGET'):
                raise ValueError('INVALID_WINDOW_KIND')
            if window.get('kind') == 'POINT_TARGET' and low != high:
                raise ValueError('POINT_TARGET_MUST_BE_SINGLE_VALUE')
        for prop in row['properties']:
            unit = 'mm' if prop['name'] == 'GROG_SIZE' else 'percent'
            if prop['unit'] != unit:
                raise ValueError('INVALID_PROPERTY_UNIT')
            low = number(prop['min'], 'property.min', high=100)
            high = number(prop['max'], 'property.max', high=100)
            if low > high:
                raise ValueError('INVERTED_PROPERTY')
            if prop['test_temperature_c'] is not None:
                number(prop['test_temperature_c'], 'test_temperature_c')
        candidate = row.get('analysis_candidate')
        if candidate:
            if candidate['status'] != 'QUARANTINED' or candidate['analysis_basis'] != 'UNKNOWN':
                raise ValueError('UNREVIEWED_CHEMISTRY_PROMOTION')
            for value in list(candidate['oxides'].values()) + [candidate['loi_pct']]:
                number(value, 'reported_analysis_percent', high=100)
    return True


def compare_reported_windows(product, stage, peak_c):
    if stage not in ('GLAZE', 'BISQUE'):
        raise ProcessInputError('INVALID_FIRING_STAGE')
    if peak_c is not None:
        number(peak_c, 'peak_c')
    claims = [deepcopy(w) for w in product['firing_windows'] if w['stage'] == stage]
    distinct = {(w['min_c'], w['max_c'], w.get('kind', 'RANGE')) for w in claims}
    result = {'engine_version': VERSION, 'product_id': product['id'], 'stage': stage,
              'source_ref': product['source_url'], 'source_claims': claims,
              'evidence_kind': 'CALCULATED', 'method_kind': 'DETERMINISTIC',
              'qualifier': 'REPORTED_RANGE_COMPARISON_NOT_COMPATIBILITY',
              'status': 'UNAVAILABLE', 'code': 'NO_REPORTED_WINDOW', 'probability': None}
    if len(distinct) > 1:
        result['code'] = 'CONFLICTING_SOURCE_WINDOWS'
    elif claims:
        w = claims[0]
        if w.get('kind') == 'POINT_TARGET':
            result['code'] = 'SINGLE_TARGET_NO_OPERATING_RANGE'
        else:
            result.update(firing_window({**w, 'product_id': product['id'],
                                         'source_ref': product['source_url'],
                                         'conditions': 'Reported; atmosphere, heatwork and test method unknown'}, peak_c))
    snapshot = {'product': product, 'stage': stage, 'peak_c': peak_c, 'version': VERSION}
    result['input_hash'] = hashlib.sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    return result


def report(bundle, catalogue):
    validate_bundle(bundle, catalogue)
    rows = bundle['products']
    candidates = [r for r in rows if r.get('analysis_candidate')]
    return {'version': VERSION, 'review_date': bundle['review_date'],
            'catalogue_products': len(catalogue), 'enriched_products': len(rows),
            'property_values': sum(len(r['properties']) for r in rows),
            'conflicting_glaze_windows': [r['id'] for r in rows if compare_reported_windows(r, 'GLAZE', 1210)['code']=='CONFLICTING_SOURCE_WINDOWS'],
            'candidate_analysis_count': len(candidates), 'new_accepted_analyses': 0,
            'reported_candidate_totals': {r['id']: round(sum(r['analysis_candidate']['oxides'].values()) + r['analysis_candidate']['loi_pct'], 8) for r in candidates},
            'research_comparisons_at_1210_c': [compare_reported_windows(r, 'GLAZE', 1210) for r in rows],
            'limitations': ['Not an adhesion, safety, surface or failure probability model.',
                            'Reuse permissions unknown; no automatic production catalogue import.',
                            'No shrinkage or absorption interpolation; methods and conditions incomplete.']}


if __name__ == '__main__':
    from research.commercial_catalogue import SEED, build
    bundle = json.loads(DATA.read_text(encoding='utf-8'))
    result = report(bundle, build(json.loads(SEED.read_text(encoding='utf-8'))))
    output = ROOT / 'data/manifests/turkey-properties-audit-2026-09-23.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='research_comparisons_at_1210_c'}, ensure_ascii=False, indent=2))
