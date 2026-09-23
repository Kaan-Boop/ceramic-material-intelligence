"""Bounded official-source acquisition. No upstream scripts are executed."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'storage/engine-dependencies/2026-09-23'
MANIFEST = ROOT / 'data/manifests/engine-dependencies-2026-09-23.json'


def fetch(url, limit=40_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': 'CeramicLab-Research/0.1'})
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read(limit + 1)
    if not data or len(data) > limit:
        raise ValueError('DOWNLOAD_SIZE_OUT_OF_BOUNDS')
    time.sleep(0.5)
    return data


def acquire():
    if MANIFEST.exists() or DEST.exists():
        raise FileExistsError('Preserve previous or partial acquisition; use a new version.')
    DEST.mkdir(parents=True)
    records = []

    def save(name, data, url, author, license_, **extra):
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(data)
        records.append(dict(source_name=name, source_url=url, source_type=extra.pop('source_type','SOFTWARE'),
                            source_author=author, source_license=license_, commercial_use_allowed='CONDITIONAL_ON_LICENSE',
                            attribution_required=True, share_alike_required='LICENSE_SPECIFIC',
                            retrieval_date=datetime.now(timezone.utc).isoformat(),
                            path=target.relative_to(ROOT).as_posix(), bytes=len(data),
                            sha256=hashlib.sha256(data).hexdigest(), **extra))
        # A partial run is traceable and never silently overwritten on retry.
        MANIFEST.write_text(json.dumps({'status':'PARTIAL','records':records},indent=2)+'\n',encoding='utf-8')

    for repo, branch, license_file, license_name, expected in [
        ('srouchier/hamopy','master','LICENSE.txt','LGPL-3.0','GNU LESSER GENERAL PUBLIC LICENSE'),
        ('LBNL-ETA/HygroThermFEM','main','LICENSE','LBNL custom BSD-style; retain complete terms','Redistribution and use'),
    ]:
        meta_url=f'https://api.github.com/repos/{repo}/commits/{branch}'
        meta=json.loads(fetch(meta_url,2_000_000))
        sha=meta['sha']
        license_url=f'https://raw.githubusercontent.com/{repo}/{sha}/{license_file}'
        license_data=fetch(license_url,200_000)
        if expected not in license_data.decode('utf-8'):
            raise ValueError('LICENSE_CHANGED_REVIEW_REQUIRED')
        slug=repo.split('/')[-1]
        save(f'{slug}/{license_file}',license_data,license_url,repo,license_name,commit=sha,status='LICENSE_RETAINED')
        url=f'https://codeload.github.com/{repo}/zip/{sha}'
        archive=fetch(url)
        if not archive.startswith(b'PK'):
            raise ValueError('EXPECTED_ZIP')
        save(f'{slug}/{sha}.zip',archive,url,repo,license_name,commit=sha,status='ARCHIVED_NOT_EXECUTED_NOT_INTEGRATED')

    requirements=[]
    for package, version, wheel_name, license_name in [
        ('CoolProp','8.0.0','coolprop-8.0.0-cp312-abi3-win_amd64.whl','MIT'),
        ('numpy','2.2.6','numpy-2.2.6-cp312-cp312-win_amd64.whl','BSD-3-Clause plus bundled dependency notices'),
    ]:
        url=f'https://pypi.org/pypi/{package}/{version}/json'
        metadata=fetch(url,3_000_000)
        meta=json.loads(metadata)
        item=next(x for x in meta['urls'] if x['filename']==wheel_name)
        if item.get('yanked'):
            raise ValueError('YANKED_WHEEL')
        data=fetch(item['url'])
        digest=hashlib.sha256(data).hexdigest()
        if digest!=item['digests']['sha256']:
            raise ValueError('PUBLISHER_HASH_MISMATCH')
        save(f'{package}/pypi-metadata.json',metadata,url,package+' contributors',license_name,status='METADATA')
        save(f'wheels/{wheel_name}',data,item['url'],package+' contributors',license_name,
             version=version,publisher_sha256=digest,status='WHEEL_HASH_VERIFIED_NOT_YET_INSTALLED')
        requirements.append(f'{package}=={version} --hash=sha256:{digest}')
    (DEST/'requirements.lock').write_text('\n'.join(requirements)+'\n',encoding='utf-8')
    MANIFEST.write_text(json.dumps({'schema_version':'engine-acquisition/1','status':'ACQUIRED',
                                   'scope':'research environment only; no production integration',
                                   'records':records},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(records),'bytes':sum(r['bytes'] for r in records),'manifest':str(MANIFEST)}))


if __name__=='__main__':
    acquire()
