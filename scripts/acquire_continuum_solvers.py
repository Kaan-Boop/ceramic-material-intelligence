"""Pinned official solver sources; archive only, no installation or execution."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'storage/continuum-solvers/2026-09-23'
MANIFEST = ROOT/'data/manifests/continuum-solvers-2026-09-23.json'
PROJECTS = [
    ('sfepy/sfepy', 'master', 'LICENSE', 'BSD-3-Clause', 'Redistribution and use', None),
    ('OpenFOAM/OpenFOAM-13', 'master', 'COPYING', 'GPL-3.0; see file notices for or-later', 'GNU GENERAL PUBLIC LICENSE', None),
    ('oomph-lib/oomph-lib', 'main', 'LICENCE', 'LGPL-2.1-or-later; third-party exceptions', 'Lesser General Public', [
        'README.md', 'demo_drivers/axisym_navier_stokes/axi_static_cap/axi_static_cap.cc',
        'demo_drivers/navier_stokes/static_cap/static_single_layer.cc',
        'demo_drivers/young_laplace/spherical_cap_in_cylinder.cc']),
    ('ElmerCSC/elmerfem', 'devel', 'LICENSE.md', 'Mixed GPL/LGPL and third-party notices; per-file review required', 'GNU GENERAL PUBLIC LICENSE', [
        'README.adoc', 'fem/src/modules/HeatSolve.F90', 'fem/src/modules/StressSolve.F90',
        'fem/src/modules/FreeSurfaceSolver.F90']),
]


def fetch(url, limit):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'CeramicLab-Research/0.2'}), timeout=60) as response:
        data = response.read(limit+1)
    if not data or len(data) > limit:
        raise ValueError('DOWNLOAD_SIZE_LIMIT')
    time.sleep(.5)
    return data


def run():
    if DEST.exists() or MANIFEST.exists():
        raise FileExistsError('Preserve prior/partial batch; do not overwrite')
    DEST.mkdir(parents=True)
    records = []
    def receipt(status):
        MANIFEST.write_text(json.dumps(dict(status=status, records=records,
            installed=False, integrated=False, source_code_executed=False), indent=2)+'\n', encoding='utf-8')
    for repo, branch, license_file, license_name, marker, selected in PROJECTS:
        metadata = json.loads(fetch(f'https://api.github.com/repos/{repo}/commits/{branch}', 2000000))
        sha = metadata['sha']
        base = f'https://raw.githubusercontent.com/{repo}/{sha}/'
        license_data = fetch(base+license_file, 200000)
        if marker not in license_data.decode('utf-8'):
            raise ValueError('LICENSE_REVIEW_REQUIRED')
        files = [(license_file, license_data, base+license_file)]
        if selected is None:
            url = f'https://codeload.github.com/{repo}/zip/{sha}'
            data = fetch(url, 180000000)
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if archive.testzip() is not None:
                    raise ValueError('ARCHIVE_CRC_FAILURE')
            files.append((sha+'.zip', data, url))
        else:
            for path in selected:
                files.append((path, fetch(base+path, 5000000), base+path))
        for name, data, url in files:
            target = DEST/repo.split('/')[-1]/name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
            records.append(dict(source_name=repo, source_author=repo+' contributors',
                source_url=url, source_type='OPEN_SOURCE_SOFTWARE', source_license=license_name,
                commercial_use_allowed='CONDITIONAL_ON_APPLICABLE_LICENSE', attribution_required=True,
                copyleft_obligations='NONE_BSD_NOTICE_REQUIRED' if repo.startswith('sfepy/') else 'REVIEW_BEFORE_DISTRIBUTION_OR_LINKING',
                retrieval_date=datetime.now(timezone.utc).isoformat(), commit=sha,
                acquisition_scope='FULL_REPOSITORY_SNAPSHOT' if selected is None else 'SELECTED_FILES_NOT_RUNNABLE_PACKAGE',
                path=target.relative_to(ROOT).as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
            receipt('PARTIAL')
        print('Acquired '+repo+' @ '+sha, flush=True)
    receipt('ACQUIRED')
    print(json.dumps(dict(files=len(records), bytes=sum(r['bytes'] for r in records))))


if __name__ == '__main__':
    run()
