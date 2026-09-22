"""Inspect known UTF-16 header only; never infer binary numeric records."""
import hashlib
import json
from pathlib import Path
import zipfile


def inspect_header(raw):
    marker = b'\x0c\x00'
    end = raw.find(marker)
    if not raw.startswith(b'\xff\xfe') or end < 0 or end > 65536 or end % 2:
        raise ValueError('UNRECOGNIZED_HEADER')
    header = raw[:end].decode('utf-16')
    # Exclude operator identity, workstation paths and instrument serial numbers.
    allowed = ('Instrument ', 'Module ', 'Size ', 'Sig', 'OrgMethod ', 'Xcomment Gas', 'Xcomment Pan:')
    return dict(header_fields=[line for line in header.splitlines() if line.startswith(allowed)],
                sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                status='QUARANTINED', reason='BINARY_RECORD_LAYOUT_NOT_VALIDATED',
                numeric_rows_validated=0, vapor_replay_allowed=False)


def main():
    manifest = json.loads(Path('data/manifests/tga-zenodo-17659041.json').read_text(encoding='utf-8'))
    entry = manifest['files'][1]
    archive = Path('storage/tga/17659041') / entry['raw_path']
    if hashlib.sha256(archive.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError('ARCHIVE_HASH_MISMATCH')
    records = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            if info.file_size > 1024*1024:
                raise ValueError('MEMBER_SIZE_LIMIT')
            records.append(dict(filename=info.filename, **inspect_header(z.read(info))))
    result = dict(source_url=manifest['source_url'], archive_sha256=entry['sha256'],
                  source_license=manifest['source_license'], records=records,
                  received=len(records), quarantined=len(records), accepted_for_engine=0,
                  numeric_missingness='NOT_ASSESSED_BINARY_FORMAT',
                  duplicates_by_content=len(records)-len({r['sha256'] for r in records}))
    target = Path('data/manifests/tga-17659041-quality.json')
    with target.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
    print(json.dumps({k:v for k,v in result.items() if k != 'records'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
