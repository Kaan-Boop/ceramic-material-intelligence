"""License-gated primary literature and pinned code selection; no code execution."""
from datetime import datetime, timezone
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from .acquire import Collector, article_authors

ROOT = Path('storage/physics-pool/2026-09-22')
MANIFEST = Path('data/manifests/physics-pool-2026-09-22.json')
PAPERS = ('PMC8063730', 'PMC11123035', 'PMC12280097')
REPOS = (
    ('TA-Instruments/tadatakit', 'b5efbc2e55fde67d492d49a3e396433ab71d4f17',
     'LICENSE', ('README.md', 'pyproject.toml', 'tadatakit/__init__.py'), 'INSTRUMENT_JSON_IMPORT'),
    ('pycalphad/pycalphad', '1606b43d9f39d897ffa66bb1a77c071fdcde5b59',
     'LICENSE.txt', ('README.rst', 'pycalphad/model.py'), 'PHASE_EQUILIBRIUM_REQUIRES_SEPARATE_TDB'),
    ('CoolProp/CoolProp', '013429639d385de51dd62182da600fd0d3488070',
     'LICENSE', ('README.md', 'include/HumidAirProp.h'), 'WATER_STEAM_AND_HUMID_AIR_PROPERTIES'),
)


def paper_metadata(raw):
    root = ET.fromstring(raw)
    meta = root.find('./front/article-meta')
    if meta is None:
        raise ValueError('ARTICLE_METADATA_REQUIRED')
    permission = meta.find('permissions')
    if permission is None or 'creativecommons.org/licenses/by/4.0/' not in ET.tostring(permission, encoding='unicode'):
        raise ValueError('CC_BY_4_LICENSE_REVIEW_REQUIRED')
    doi = meta.findtext("article-id[@pub-id-type='doi']")
    if not doi:
        raise ValueError('DOI_REQUIRED')
    title = ''.join(meta.find('title-group/article-title').itertext())
    return root, dict(source_name=title, source_author=article_authors(meta),
                      source_url='https://doi.org/' + doi, source_type='PRIMARY_RESEARCH_ARTICLE',
                      source_license='CC-BY-4.0', license_evidence=ET.tostring(permission, encoding='unicode'))


def table_extract(root):
    # Preserve structure, captions and footnotes; no unit guessing or model fitting.
    return [dict(id=t.get('id'), label=t.findtext('label'),
                 caption=' '.join(t.find('caption').itertext()) if t.find('caption') is not None else None,
                 xml=ET.tostring(t, encoding='unicode')) for t in root.iter('table-wrap')]


def acquire(root=ROOT, manifest=MANIFEST):
    root, manifest = Path(root), Path(manifest)
    if manifest.exists():
        raise ValueError('EXISTING_MANIFEST_WILL_NOT_BE_OVERWRITTEN')
    c = Collector(root)
    sources = []
    for pmc in PAPERS:
        url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML'
        raw, final = c.fetch(url)
        article, source = paper_metadata(raw)
        c.save(pmc, 'article.xml', url, raw, final)
        tables = table_extract(article)
        path = root / 'processed' / (pmc + '-tables.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(source_ref=source['source_url'], raw_sha256=c.entries[-1]['sha256'],
                       status='STRUCTURAL_EXTRACTION_NOT_NORMALIZED', tables=tables)
        encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
        if path.exists() and path.read_bytes() != encoded:
            raise ValueError('DERIVED_ARTIFACT_CONFLICT')
        if not path.exists():
            with path.open('xb') as stream:
                stream.write(encoded)
        sources.append(dict(source, source_id=pmc, table_count=len(tables),
                            use_status='RESEARCH_REFERENCE_NOT_ENGINE_PARAMETERS',
                            processed_path=path.as_posix()))
    for repo, commit, license_file, files, role in REPOS:
        prefix = f'https://raw.githubusercontent.com/{repo}/{commit}/'
        raw, final = c.fetch(prefix + license_file)
        if b'Permission is hereby granted, free of charge' not in raw:
            raise ValueError('MIT_LICENSE_REVIEW_REQUIRED')
        c.save(repo, license_file, prefix + license_file, raw, final)
        for file in files:
            c.download(repo, file, prefix + file)
        sources.append(dict(source_id=repo, source_name=repo, source_author='Copyright holders in archived license',
                            source_url='https://github.com/' + repo, source_type='PINNED_CODE_SELECTION',
                            source_license='MIT', license_evidence=prefix + license_file, commit=commit,
                            role=role, use_status='ARCHIVED_NOT_INSTALLED_OR_EXECUTED'))
    now = datetime.now(timezone.utc).isoformat()
    for source in sources:
        source.update(commercial_use_allowed='ALLOWED_WITH_LICENSE_CONDITIONS', attribution_required=True,
                      share_alike_required=False, retrieval_date=now,
                      rights_scope='Selected files only; third-party material and external datasets require separate review')
    result = dict(schema_version='physics-pool/1', sources=sources, files=c.entries,
                  source_count=len(sources), file_count=len(c.entries), bytes=sum(e['bytes'] for e in c.entries),
                  production_parameters_added=0, raw_measurement_series_imported=0,
                  blocked_candidates=[dict(source_url='https://doi.org/10.11583/dtu.30157066.v1',
                      reason='Metadata reviewed CC-BY-4.0; official download redirects to s3q.ait.dtu.dk which failed TLS certificate verification'),
                      dict(source_url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8063730/supplementaryFiles',
                           reason='Read timeout; supplementary archive not acquired')])
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    return result


if __name__ == '__main__':
    r = acquire()
    print(json.dumps({k:r[k] for k in ('source_count','file_count','bytes')}, indent=2))
