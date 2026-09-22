"""Bounded official CC-BY thermal archive acquisition; no archive extraction."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
from .acquire import Collector


def main():
    path = Path('data/manifests/tga-zenodo-17659041.json')
    if path.exists():
        raise ValueError('RECEIPT_ALREADY_EXISTS')
    c = Collector('storage/tga/17659041')
    url = 'https://zenodo.org/api/records/17659041'
    raw, final = c.fetch(url)
    data = json.loads(raw)
    meta = data['metadata']
    if meta['license']['id'] != 'cc-by-4.0' or meta['access_right'] != 'open':
        raise ValueError('RIGHTS_REVIEW_REQUIRED')
    c.save('zenodo-17659041', 'metadata.json', url, raw, final)
    file = next(f for f in data['files'] if f['key'] == 'Thermal analysis.zip')
    archive, final = c.fetch(file['links']['self'])
    if len(archive) != file['size'] or 'md5:'+hashlib.md5(archive).hexdigest() != file['checksum']:
        raise ValueError('PUBLISHER_CHECKSUM_MISMATCH')
    c.save('zenodo-17659041', file['key'], file['links']['self'], archive, final)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        inventory = [dict(name=i.filename, bytes=i.file_size) for i in z.infolist()]
    receipt = dict(source_name=meta['title'], source_url='https://zenodo.org/records/17659041',
                   source_type='ACADEMIC_DATASET', source_author=[a['name'] for a in meta['creators']],
                   source_license='CC-BY-4.0', commercial_use_allowed='ALLOWED_WITH_ATTRIBUTION',
                   attribution_required=True, share_alike_required=False,
                   retrieval_date=c.entries[-1]['retrieved_at'], files=c.entries, inventory=inventory,
                   intended_use='RESEARCH_ONLY_PENDING_SCHEMA_REVIEW', production_analyses_added=0)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
    print(json.dumps(inventory, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
