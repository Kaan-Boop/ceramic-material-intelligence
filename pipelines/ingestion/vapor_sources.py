"""Archive a small official Cantera source selection; never execute it."""
import json
from pathlib import Path
from .acquire import Collector


def main():
    root = Path('storage/vapor/sources')
    manifest = Path('data/manifests/vapor-cantera-2026-09-22.json')
    if manifest.exists():
        raise ValueError('RECEIPT_ALREADY_EXISTS')
    collector = Collector(root)
    raw, _ = collector.fetch('https://api.github.com/repos/Cantera/cantera/commits/v3.2.0')
    commit = json.loads(raw)['sha']
    prefix = f'https://raw.githubusercontent.com/Cantera/cantera/{commit}/'
    license_raw = collector.download('cantera', 'License.txt', prefix + 'License.txt')
    if b'Redistribution and use in source and binary forms' not in license_raw:
        raise ValueError('LICENSE_REVIEW_REQUIRED')
    for filename in ('README.rst', 'samples/python/thermo/vapordome.py'):
        collector.download('cantera', filename, prefix + filename)
    receipt = dict(source_name='Cantera', source_url='https://github.com/Cantera/cantera',
                   source_author='Cantera Developers and copyright holders in License.txt',
                   source_type='PINNED_CODE_SELECTION', source_license='BSD-3-Clause',
                   commercial_use_allowed='ALLOWED_WITH_LICENSE_CONDITIONS', attribution_required=True,
                   share_alike_required=False, commit=commit, requested_tag='v3.2.0',
                   retrieval_date=collector.entries[-1]['retrieved_at'], files=collector.entries,
                   integration='REFERENCE_ONLY_NOT_INSTALLED_OR_EXECUTED',
                   rights_scope='Selected code only; external mechanisms/data require separate review')
    with manifest.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2)
    print(json.dumps({'commit': commit, 'files': len(collector.entries), 'manifest': str(manifest)}))


if __name__ == '__main__':
    main()
