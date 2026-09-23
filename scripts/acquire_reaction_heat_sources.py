"""Official-source archive; bounded requests, pinned commits, no source execution."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'storage/reaction-heat-pool/2026-09-23'
MANIFEST=ROOT/'data/manifests/reaction-heat-acquisition-2026-09-23.json'


def fetch(url,limit=60_000_000):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CeramicLab-Research/0.1'}),timeout=60) as r:
        data=r.read(limit+1)
    if not data or len(data)>limit: raise ValueError('DOWNLOAD_SIZE_LIMIT')
    time.sleep(0.4)
    return data


def run():
    if DEST.exists() or MANIFEST.exists(): raise FileExistsError('Preserve partial acquisition; select new batch')
    DEST.mkdir(parents=True)
    records=[]
    def save(name,data,url,license_,author,**extra):
        path=DEST/name
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f: f.write(data)
        records.append(dict(source_name=name,source_url=url,source_author=author,
            source_type='OPEN_SOURCE_SOFTWARE',source_license=license_,commercial_use_allowed='WITH_LICENSE_CONDITIONS',
            attribution_required=True,share_alike_required=False,retrieval_date=datetime.now(timezone.utc).isoformat(),
            path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
            status='ARCHIVED_NOT_EXECUTED',rights_scope='CODE; THIRD_PARTY_DATA_REQUIRES_SEPARATE_REVIEW',**extra))
        MANIFEST.write_text(json.dumps({'status':'PARTIAL','records':records},indent=2)+'\n',encoding='utf-8')
    for repo,ref,license_file,license_,marker,mode in [
        ('Cantera/cantera','v3.2.0','License.txt','BSD-3-Clause','Redistribution and use','ZIP'),
        ('usnistgov/fipy','master','LICENSE.rst','NIST terms of use','without fee is hereby granted','ZIP'),
        ('pycalphad/pycalphad','develop','LICENSE.txt','MIT','Permission is hereby granted','ZIP'),
        ('CalebBell/thermo','master','LICENSE.txt','MIT','Permission is hereby granted','SELECTED'),
        ('CalebBell/chemicals','master','LICENSE.txt','MIT','Permission is hereby granted','SELECTED'),
    ]:
        sha=json.loads(fetch(f'https://api.github.com/repos/{repo}/commits/{ref}',2_000_000))['sha']
        base=f'https://raw.githubusercontent.com/{repo}/{sha}/'
        license_data=fetch(base+license_file,200_000)
        if marker not in license_data.decode(): raise ValueError('LICENSE_REVIEW_NEEDED')
        slug=repo.split('/')[-1]
        save(f'{slug}/{license_file}',license_data,base+license_file,license_,repo,commit=sha)
        if mode=='ZIP':
            url=f'https://codeload.github.com/{repo}/zip/{sha}'
            archive=fetch(url)
            if not archive.startswith(b'PK'): raise ValueError('EXPECTED_ZIP')
            save(f'{slug}/{sha}.zip',archive,url,license_,repo,commit=sha)
        else:
            paths=['README.rst',f'{slug}/heat_capacity.py']
            if slug=='chemicals': paths.append('chemicals/reaction.py')
            for name in paths:
                save(f'{slug}/{name}',fetch(base+name,3_000_000),base+name,license_,repo,commit=sha)
        print(f'Archived {repo} {sha}',flush=True)
    lock=[]
    packages=[('cantera','3.2.0','cp312-cp312-win_amd64.whl','BSD-3-Clause'),
              ('numpy','2.2.6','cp312-cp312-win_amd64.whl','BSD-3-Clause and bundled notices'),
              ('ruamel.yaml','0.18.16','py3-none-any.whl','MIT'),
              ('ruamel.yaml.clib','0.2.12','cp312-cp312-win_amd64.whl','MIT'),
              ('typing_extensions','4.15.0','py3-none-any.whl','PSF-2.0')]
    for package,version,suffix,license_ in packages:
        url=f'https://pypi.org/pypi/{package}/{version}/json'
        metadata=fetch(url,3_000_000)
        meta=json.loads(metadata)
        item=next(x for x in meta['urls'] if x['filename'].endswith(suffix))
        if item.get('yanked'): raise ValueError('YANKED_RELEASE')
        # Reuse an identical reviewed NumPy wheel, rather than downloading twice.
        prior=ROOT/'storage/engine-dependencies/2026-09-23/wheels'/item['filename']
        data=prior.read_bytes() if prior.exists() else fetch(item['url'])
        sha=hashlib.sha256(data).hexdigest()
        if sha!=item['digests']['sha256']: raise ValueError('PUBLISHER_HASH_MISMATCH')
        save(f'{package}/pypi.json',metadata,url,license_,package+' contributors',version=version)
        save(f'wheels/{item["filename"]}',data,item['url'],license_,package+' contributors',version=version,publisher_sha256=sha,reused=prior.exists())
        lock.append(f'{package}=={version} --hash=sha256:{sha}')
    (DEST/'requirements.lock').write_text('\n'.join(lock)+'\n',encoding='utf-8')
    MANIFEST.write_text(json.dumps({'schema_version':'reaction-heat-pool/1','status':'ACQUIRED',
        'records':records,'software_repositories':5,'production_integration':False},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(records),'bytes':sum(r['bytes'] for r in records)}))


if __name__=='__main__': run()
