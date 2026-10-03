"""Offline, conservative title screening. Never labels a paper read or verified."""
import csv
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'storage/research/literature-2026-09-27'
TYPES = {'journal-article', 'proceedings-article', 'report', 'posted-content', 'dissertation'}
EXCLUDE = re.compile(r'cheminform abstract|correction to|erratum|corrigendum|retract|polypropylene|dental|dentistry|implant|electro.osmotic|glass ceiling|glass eels', re.I)
DIRECT = re.compile(r'glaz|porcelain|stoneware|earthenware|engob|kaolin|ceramic tile|ceramic drying|clay drying|frit|seramik|釉|глазур', re.I)


def screen(record):
    if record['publication_type'] not in TYPES:
        return 'OTHER_DOCUMENT_TYPE'
    if EXCLUDE.search(record['title']):
        return 'LIKELY_OFF_SCOPE_OR_SECONDARY_NOTICE'
    if record['title_screen'] != 'DOMAIN_TERM_PRESENT':
        return 'MANUAL_TITLE_REVIEW_REQUIRED'
    return 'DIRECT_TOPIC_CANDIDATE' if DIRECT.search(record['title']) else 'ADJACENT_MATERIALS_CANDIDATE'


def main():
    rows = json.loads((OUT/'catalog.json').read_text(encoding='utf-8'))
    for row in rows:
        row['screening_bucket'] = screen(row)
    selected = [r for r in rows if r['screening_bucket'].endswith('_CANDIDATE')]
    selected.sort(key=lambda r: (r['screening_bucket'] != 'DIRECT_TOPIC_CANDIDATE', not bool(r['reported_licenses']), r['doi']))
    (OUT/'reading-queue.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'reading-queue.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        fields=['doi','title','publication_type','screening_bucket','reading_status']
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for r in selected:
            writer.writerow({k: "'"+r[k] if isinstance(r[k],str) and r[k][:1] in '=+-@' else r[k] for k in fields})
    summary=dict(total=len(rows), buckets=dict(Counter(r['screening_bucket'] for r in rows)),
                 queued_dois=len(selected), queued_distinct_normalized_titles=len({r['title_key'] for r in selected}),
                 all_dois_unique=len({r['doi'] for r in rows})==len(rows),
                 all_reading_status_metadata_only=all(r['reading_status']=='METADATA_ONLY' for r in rows),
                 all_training_disabled=all(r['training_allowed'] is False for r in rows),
                 fulltexts_read_this_batch=0, extracted_experiments_this_batch=0,
                 screening_caveat='Title heuristics only; neither relevance approval nor independent-study counting.')
    (OUT/'screening-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__': main()
