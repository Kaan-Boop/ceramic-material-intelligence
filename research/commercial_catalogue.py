"""Research-only catalogue identities. Never resolves a chemistry analysis ID.

Seed facts were manually reviewed from named public pages, not scraped. This
builder does not fetch, infer ingredient percentages, or grant upstream rights.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / 'data/research/commercial-products-seed.json'


def canonical(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def build(seed):
    records = []
    keys = set()
    for group in seed['groups']:
        for item in group['products']:
            code, name = item.split('|', 1)
            # Kind prevents a glaze and clay with coincident codes being merged.
            key = (canonical(group['brand']), group['kind'], canonical(code or name))
            if key in keys:
                raise ValueError('DUPLICATE_PRODUCT_REQUIRES_SOURCE_RELATION')
            keys.add(key)
            flags = list(group.get('flags', []))
            if not code:
                flags.append('PRODUCT_CODE_NOT_REPORTED')
            records.append({
                'id': 'product-' + sha256('|'.join(key).encode()).hexdigest()[:20],
                'brand': group['brand'], 'product_code': code or None, 'source_name_verbatim': name,
                'entity_kind': group['kind'], 'discovery_market': group['market'],
                'manufacturing_country': None, 'manufacturing_country_missing_reason': 'NOT_VERIFIED_PER_PRODUCT',
                'identity_status': 'LISTED_IN_REVIEWED_SOURCE', 'commercial_popularity_rank': None,
                'record_layer': 'RESEARCH_INDEX_NOT_PRODUCTION_DATA',
                'ingredient_recipe': None, 'oxide_analysis': None, 'analysis_basis': 'UNKNOWN',
                'chemistry_engine_eligible': False, 'chemistry_missing_reason': 'NO_ACCEPTED_VERSIONED_ANALYSIS',
                'quality_flags': flags,
                'source_id': group['source_id'], 'source_name': group['publisher'],
                'source_url': group['url'], 'source_type': group['source_type'],
                'source_author': group['publisher'], 'source_license': 'UNKNOWN_REUSE_RIGHTS',
                'commercial_use_allowed': 'UNKNOWN', 'research_republication_allowed': 'UNKNOWN',
                'attribution_required': 'UNKNOWN', 'share_alike_required': 'UNKNOWN',
                'retrieval_date': seed['review_date'], 'source_document_date': group.get('document_date'),
                'rights_layer': 'UNKNOWN_LICENSE', 'training_allowed': 'UNKNOWN',
                'full_source_archived': False, 'raw_source_sha256': None,
                'acquisition_method': 'MANUAL_BIBLIOGRAPHIC_IDENTITY_INDEX',
            })
    return records


def audit(records):
    ids = [r['id'] for r in records]
    return {'schema_version': 'commercial-index-audit/1', 'grain': 'one brand + product code/name + entity kind',
            'records': len(records), 'unique_ids': len(set(ids)), 'duplicate_ids': len(ids)-len(set(ids)),
            'brands_with_indexed_products': len({r['brand'] for r in records}),
            'by_kind': dict(Counter(r['entity_kind'] for r in records)),
            'clay_body_brands': len({r['brand'] for r in records if r['entity_kind']=='CLAY_BODY'}),
            'by_market_and_kind': {market:dict(Counter(r['entity_kind'] for r in records if r['discovery_market']==market)) for market in ('TR','EUROPE','USA')},
            'by_discovery_market': dict(Counter(r['discovery_market'] for r in records)),
            'ingredient_recipes_available': sum(r['ingredient_recipe'] is not None for r in records),
            'accepted_oxide_analyses': sum(r['oxide_analysis'] is not None for r in records),
            'engine_eligible': sum(r['chemistry_engine_eligible'] for r in records),
            'unknown_reuse_rights': sum(r['rights_layer']=='UNKNOWN_LICENSE' for r in records),
            'source_url_missing': sum(not r.get('source_url') for r in records),
            'quality_flags': dict(Counter(f for r in records for f in r['quality_flags'])),
            'temporal_limit': 'Single review batch; no trend or complete market coverage inferred',
            'target': {'clay_brands_per_region':20,'additional_clay_products':100,'powder_glazes':100,'total_records_minimum':1001},
            'target_completed': False}


if __name__ == '__main__':
    records = build(json.loads(SEED.read_text(encoding='utf-8')))
    output = ROOT / 'data/research/commercial-products-index.json'
    output.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report = audit(records)
    (ROOT / 'data/manifests/commercial-catalogue-audit-2026-09-22.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
