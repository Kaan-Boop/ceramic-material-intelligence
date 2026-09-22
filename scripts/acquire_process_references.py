"""Small licensed reference acquisition, not crawling or executing upstream code."""
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '2c7b65d2922066b01b668e392bfec06a0f1aa431'
PAPER = 'https://www.jstage.jst.go.jp/article/jcersj2/130/3/130_21162'


def acquire():
    destination = ROOT / 'storage/process-pool/2026-09-22'
    manifest = ROOT / 'data/manifests/process-acquisition-2026-09-22.json'
    if manifest.exists():
        raise FileExistsError('Existing acquisition is immutable; choose a new version.')
    entries = [(f'amorphouspy/{name}', f'https://raw.githubusercontent.com/glasagent/amorphouspy/{COMMIT}/{name}',
                'Apache-2.0', f'https://github.com/glasagent/amorphouspy/blob/{COMMIT}/LICENSE',
                'amorphouspy contributors', 'OPEN_SOURCE_REFERENCE') for name in ['LICENSE', 'README.md', 'pyproject.toml']]
    entries.append(('kasama-celadon-2022.pdf', PAPER + '/_pdf/-char/en', 'CC-BY-4.0',
                    PAPER + '/_article/-char/en', 'Ojima et al.; Ceramic Society of Japan', 'PAPER_NOT_EXTRACTED'))
    records = []
    for name, url, license_, evidence, author, kind in entries:
        target = destination / name
        if target.exists():
            raise FileExistsError(f'Partial acquisition preserved: {target}')
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'CeramicLab-Research/0.1'}), timeout=40) as response:
            body = response.read(4_000_001)
        if len(body) > 4_000_000 or not body:
            raise ValueError('Invalid download size')
        if name.endswith('.pdf') and not body.startswith(b'%PDF'):
            raise ValueError('Expected PDF, not a challenge page')
        if name.endswith('LICENSE') and b'Apache License' not in body:
            raise ValueError('License changed; review required')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        records.append(dict(source_name=name, source_url=url, source_type=kind, source_author=author,
                            source_license=license_, commercial_use_allowed='ALLOWED_WITH_LICENSE_CONDITIONS',
                            attribution_required=True, share_alike_required=False,
                            retrieval_date=datetime.now(timezone.utc).isoformat(), license_evidence=evidence,
                            path=target.relative_to(ROOT).as_posix(), bytes=len(body),
                            sha256=hashlib.sha256(body).hexdigest(),
                            commit=COMMIT if name.startswith('amorphouspy/') else None,
                            status='ARCHIVED_NOT_EXECUTED_NOT_MODEL_TRAINING'))
        time.sleep(1)
    manifest.write_text(json.dumps(dict(schema_version='process-source-pool/1', records=records), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(files=len(records), bytes=sum(r['bytes'] for r in records))))


if __name__ == '__main__':
    acquire()
