"""Bounded Crossref discovery; metadata is NOT full-text review or training data.

Run: python scripts/collect_literature.py --fetch
Omit --fetch to regenerate catalog from immutable cached API responses.
"""
import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'storage/research/literature-2026-09-27'
QUERIES = {
    'glaze-chemistry': ['ceramic glaze chemistry', 'ceramic glaze oxide composition', 'ceramic frit formulation'],
    'viscosity': ['silicate melt viscosity', 'borosilicate glass viscosity', 'porcelain stoneware melt viscosity'],
    'surface-tension': ['silicate melt surface tension', 'ceramic glaze wetting contact angle'],
    'thermal': ['ceramic kiln heat transfer', 'porcelain thermal conductivity', 'ceramic firing numerical simulation'],
    'drying': ['clay drying moisture transport', 'ceramic drying numerical model'],
    'reactions': ['kaolinite dehydroxylation kinetics', 'clay carbonate decomposition thermal analysis'],
    'sintering': ['porcelain stoneware sintering kinetics', 'clay vitrification shrinkage', 'ceramic tile densification porosity'],
    'interface': ['glaze body interface diffusion', 'ceramic glaze adhesion'],
    'stress': ['glaze crazing residual stress', 'porcelain thermal expansion cristobalite', 'ceramic thermal shock cracking'],
    'defects': ['ceramic glaze pinholes blistering', 'ceramic tile pyroplastic deformation', 'clay black core bloating'],
    'crystals': ['crystalline glaze zinc silicate', 'porcelain mullite crystallization', 'ceramic glaze devitrification'],
    'color': ['ceramic pigment glaze color', 'iron oxide glaze reduction atmosphere'],
    'layers': ['ceramic engobe glaze compatibility', 'multilayer ceramic glaze thermal stress'],
    'metal': ['ceramic metal interface thermal stress'],
    'informatics': ['glass viscosity machine learning', 'ceramic glaze machine learning'],
    'theses': ['ceramic glaze', 'porcelain sintering', 'clay drying', 'glass viscosity'],
    'regional': ['seramik sır', '陶瓷 釉', 'セラミックス 釉薬', 'керамическая глазурь'],
}
DOMAIN = re.compile(r'ceramic|glaz|porcelain|stoneware|earthenware|kaolin|clay|silicate|glass|mullite|frit|engob|seramik|陶|瓷|釉|セラミ|керами|глазур', re.I)


def title_key(title):
    return re.sub(r'\W+', '', title.casefold())


def main(fetch=False):
    OUT.mkdir(parents=True, exist_ok=True)
    rawdir = OUT / 'raw'
    rawdir.mkdir(exist_ok=True)
    records, receipts, errors = {}, [], []
    retrieved = 0
    for topic, queries in QUERIES.items():
        for query in queries:
            params = {'query.bibliographic': query, 'rows': 100,
                      'filter': 'until-pub-date:2026-09-27',
                      'select': 'DOI,title,author,issued,type,license,link,publisher,container-title,relation,update-to'}
            if topic == 'theses':
                params['filter'] += ',type:dissertation'
            url = 'https://api.crossref.org/works?' + urlencode(params)
            key = hashlib.sha256(url.encode()).hexdigest()
            rawpath = rawdir / (key + '.json')
            sidecar = rawdir / (key + '.receipt.json')
            if not rawpath.exists():
                if not fetch:
                    errors.append({'query': query, 'error': 'NOT_FETCHED'})
                    continue
                try:
                    for attempt in range(3):
                        try:
                            with urlopen(Request(url, headers={'User-Agent': 'CeramicLabLiterature/0.1 (metadata research; serial requests)'}), timeout=45) as resp:
                                raw = resp.read(12*1024*1024+1)
                                if len(raw)>12*1024*1024:
                                    raise ValueError('RESPONSE_TOO_LARGE')
                                if resp.url.split('/')[2] != 'api.crossref.org':
                                    raise ValueError('UNEXPECTED_RESPONSE_HOST')
                            parsed = json.loads(raw)
                            if not isinstance(parsed.get('message', {}).get('items'), list):
                                raise ValueError('INVALID_RESPONSE_SCHEMA')
                            break
                        except HTTPError as error:
                            if error.code not in (429, 502, 503, 504) or attempt == 2:
                                raise
                            delay = min(55, max(10, int(error.headers.get('Retry-After', '10'))))
                            time.sleep(delay)
                    rawpath.write_bytes(raw)
                    sidecar.write_text(json.dumps({'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'sha256': hashlib.sha256(raw).hexdigest()}, indent=2), encoding='utf-8')
                    time.sleep(2)
                except Exception as error:
                    errors.append({'query': query, 'error': str(error)})
                    print('FAILED', query, str(error), flush=True)
                    continue
            raw = rawpath.read_bytes()
            receipt = json.loads(sidecar.read_text(encoding='utf-8'))
            if hashlib.sha256(raw).hexdigest() != receipt['sha256']:
                raise ValueError('RAW_HASH_MISMATCH')
            items = json.loads(raw)['message']['items']
            receipts.append(dict(receipt, query=query, topic=topic, record_count=len(items), raw_path=str(rawpath.relative_to(ROOT))))
            retrieved += len(items)
            for item in items:
                doi = item.get('DOI', '').strip().lower()
                title = ' '.join(item.get('title', []))
                if not doi or not title:
                    continue
                if doi not in records:
                    records[doi] = dict(doi=doi, title=title, title_key=title_key(title),
                        authors=item.get('author', []), date=item.get('issued', {}).get('date-parts'),
                        publication_type=item.get('type'), language=item.get('language'),
                        publisher=item.get('publisher'), venue=item.get('container-title', []),
                        reported_licenses=item.get('license', []), reported_links=item.get('link', []),
                        relations=item.get('relation', {}), updates=item.get('update-to', []),
                        topics=[], query_refs=[],
                        title_screen='DOMAIN_TERM_PRESENT' if DOMAIN.search(title) else 'REVIEW_REQUIRED',
                        relevance_status='NOT_MANUALLY_REVIEWED', reading_status='METADATA_ONLY',
                        extraction_status='NOT_EXTRACTED', fulltext_rights='UNREVIEWED', training_allowed=False)
                record = records[doi]
                if topic not in record['topics']:
                    record['topics'].append(topic)
                record['query_refs'].append(key)
            print(topic, query, 'unique_DOIs=', len(records), flush=True)
    rows = sorted(records.values(), key=lambda row: row['doi'])
    titles = Counter(r['title_key'] for r in rows)
    for row in rows:
        row['possible_title_duplicate'] = titles[row['title_key']] > 1
    stats = dict(retrieved_records=retrieved, unique_dois=len(rows), duplicate_doi_occurrences=retrieved-len(rows),
                 domain_title_candidates=sum(r['title_screen']=='DOMAIN_TERM_PRESENT' for r in rows),
                 thesis_records=sum(r['publication_type']=='dissertation' for r in rows),
                 fulltexts_read=0, experimental_datasets_extracted=0,
                 records_with_reported_license=sum(bool(r['reported_licenses']) for r in rows),
                 language_status='NOT_REQUESTED_API_SELECT_UNSUPPORTED',
                 possible_title_duplicate_records=sum(r['possible_title_duplicate'] for r in rows),
                 types=dict(Counter(r['publication_type'] for r in rows)),
                 topic_counts={t: sum(t in r['topics'] for r in rows) for t in QUERIES},
                 errors=errors, successful_queries=len(receipts))
    (OUT/'catalog.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT/'receipt.json').write_text(json.dumps(dict(statistics=stats, queries=receipts), ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['doi', 'title', 'publication_type', 'language', 'topics', 'title_screen', 'reading_status', 'fulltext_rights']
    with (OUT/'catalog.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            selected = {key: row[key] for key in fields}
            selected['topics'] = '|'.join(selected['topics'])
            # Guard spreadsheet formula execution in bibliographic text.
            writer.writerow({k: "'"+v if isinstance(v,str) and v[:1] in '=+-@' else v for k,v in selected.items()})
    print(json.dumps(stats, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true')
    main(parser.parse_args().fetch)
