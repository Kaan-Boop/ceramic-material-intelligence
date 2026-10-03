"""Download reviewed, pinned UI references only; never execute upstream code."""
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('radix-ui/primitives', 'f7ecd5ab16f5e1e820eb5786a1419a98a2d594ae', 'MIT', [
        'LICENSE', 'packages/react/dialog/src/dialog.tsx',
        'packages/react/popover/src/popover.tsx', 'packages/react/tooltip/src/tooltip.tsx']),
    ('lucide-icons/lucide', 'f06ac67e33d645c40b8ce19a0419c85c5d7dd751', 'ISC + MIT for Feather-derived icons', [
        'LICENSE', 'icons/info.svg', 'icons/plus.svg', 'icons/flask-conical.svg',
        'icons/layers.svg', 'icons/chevron-down.svg']),
]


def acquire():
    destination = ROOT / 'storage/design-pool/2026-09-22'
    manifest_path = ROOT / 'data/manifests/ui-references-2026-09-22.json'
    if manifest_path.exists():
        raise FileExistsError('Existing manifest preserved; choose a new acquisition version.')
    records = []
    for repo, commit, license_name, files in SOURCES:
        for name in files:
            url = f'https://raw.githubusercontent.com/{repo}/{commit}/{name}'
            request = urllib.request.Request(url, headers={'User-Agent': 'CeramicLab-UI-Research/0.1'})
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read(1_000_001)
            if len(body) > 1_000_000:
                raise ValueError('File size limit exceeded')
            target = destination / repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            records.append({
                'source_name': repo, 'source_url': url, 'source_type': 'PINNED_OPEN_SOURCE_CODE',
                'source_author': 'WorkOS' if repo.startswith('radix') else 'Lucide contributors; Cole Bemis for Feather-derived icons',
                'source_license': license_name, 'commercial_use_allowed': 'ALLOWED_WITH_NOTICE_RETENTION',
                'attribution_required': True, 'share_alike_required': False,
                'retrieval_date': datetime.now(timezone.utc).isoformat(), 'commit': commit,
                'path': target.relative_to(ROOT).as_posix(), 'bytes': len(body),
                'sha256': hashlib.sha256(body).hexdigest(),
                'license_evidence': f'https://github.com/{repo}/blob/{commit}/LICENSE',
                'status': 'REFERENCE_ONLY_NOT_INSTALLED',
            })
            time.sleep(1)
    result = {'schema_version': 'ui-pool/1', 'sources': 2, 'files': records,
              'notes': ['Selected files, not full repositories.', 'Apple/Digitalfire pages are research references only, not copied datasets.']}
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sources': 2, 'files': len(records), 'bytes': sum(r['bytes'] for r in records)}))


if __name__ == '__main__':
    acquire()
