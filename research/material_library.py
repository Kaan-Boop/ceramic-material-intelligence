"""Local research projections; never adds analyses to the chemistry resolver.

Commercial entries expose bibliographic identities and limited existing factual
notes only, not source pages/photos/recipes. Unknown rights remain unknown.
"""
import json
from pathlib import Path
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[1] / 'data'

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def build_library(theoretical):
    records = []
    for m in theoretical:
        records.append(dict(id=m['analysis_id'], name=m['name'], brand='Teorik referans', kind='IDEAL_MATERIAL',
            formula=m['formula'], oxides=m['oxides'], loi=m['loi_pct'], basis=m['basis'], status='THEORETICAL',
            engine_eligible=True, source_url=m['source_url'], source_name=m['source_ref'], license='PROJECT_THEORETICAL_FIXTURE',
            review_date=None, version=m['version'], windows=[], uses=[], flags=[],
            note='İdeal formülden hesaplanan kuru baz oksit muhasebesi; ticari ürün analizi veya pişmiş faz dağılımı değildir.'))
    properties = read('research/turkey-body-properties-2026-09-23.json')
    for r in read('research/commercial-products-index.json'):
        # Exact URL or exact brand + recorded catalogue key; no fuzzy matching.
        p = next((p for p in properties['products'] if p['source_url']==r['source_url'] or
                  (p['brand']==r['brand'] and p['catalogue_key']==r['source_name_verbatim'])), {})
        candidate = p.get('analysis_candidate', {})
        records.append(dict(id=r['id'],name=r['source_name_verbatim'],brand=r['brand'],kind=r['entity_kind'],formula=None,
            oxides=candidate.get('oxides',{}),loi=candidate.get('loi_pct'),basis='UNKNOWN',status='RESEARCH_ONLY',engine_eligible=False,
            source_url=p.get('source_url',r['source_url']),source_name=r['source_name'],license=r['source_license'],review_date=r['retrieval_date'],version='research-index/1',
            windows=p.get('firing_windows',[]),uses=p.get('reported_uses',[]),
            flags=sorted(set(r['quality_flags']+p.get('flags',[])+candidate.get('flags',[]))),
            note=('Üretici açıklamasında feldspatik ve silisli hammaddeler belirtiliyor; oranlar açıklanmıyor.' if p.get('composition_note') else 'Tam hammadde reçetesi ve kabul edilmiş analiz bulunmuyor.')
                 + ' Yerel araştırma kaydı; yeniden yayınlama ve eğitim izni doğrulanmadı.'))
    studies = read('reference/study-material-candidates-v1.json')
    for r in studies['records']:
        source = studies['sources'][r['source_id']]
        if source['source_license']!='CC-BY-4.0':
            continue
        vals = {v['reported_as']:float(v['value']) for v in r['measurements'] if v['value'] is not None and 'O' in v['reported_as'] and v['reported_as'] not in ('LOI','Others','Total')}
        records.append(dict(id='study-'+sha256(r['id'].encode()).hexdigest()[:20],name=r['name_as_reported'],brand=r.get('manufacturer_as_reported') or 'Araştırma numunesi',kind='STUDY_MATERIAL',formula=None,
            oxides=vals,loi=next((float(v['value']) for v in r['measurements'] if v['reported_as']=='LOI' and v['value'] is not None),None),
            basis=r['analysis_basis'],status='QUARANTINED',engine_eligible=False,source_url=source['source_url'],source_name=source['source_name']+' — '+source['source_author'],
            license=source['source_license'],review_date=source['retrieval_date'],version=str(r['version']),windows=[],uses=[],flags=r['quality_flags'],
            note='Çalışmaya özgü numune; güncel ticari ürün analizi değildir. '+r['source_locator']+'. Eksik oksit sıfır kabul edilmez; analiz bazı doğrulanmadan hesapta kullanılamaz. Oksit dışı S ve Cl gibi raporlanan alanlar bu oksit grafiğine dahil edilmez; özgün araştırma kaydında korunur.'))
    assert len({r['id'] for r in records})==len(records)
    return records
