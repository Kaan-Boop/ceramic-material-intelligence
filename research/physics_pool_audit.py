"""Offline checks for this source wave; not physical model validation."""
import hashlib
import json
from pathlib import Path
from pipelines.ingestion.moisture_observations import normalize


def audit():
    m = json.loads(Path('data/manifests/physics-pool-2026-09-22.json').read_text(encoding='utf-8'))
    root = Path('storage/physics-pool/2026-09-22')
    for entry in m['files']:
        raw = (root / entry['raw_path']).read_bytes()
        if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('SOURCE_INTEGRITY_FAILURE')
    source = next(s for s in m['sources'] if s['source_id'] == 'PMC11123035')
    entry = next(e for e in m['files'] if e['source_id'] == 'PMC11123035')
    stored = json.loads(Path('data/reference/moisture-study-observations-v1.json').read_text(encoding='utf-8'))
    replay = normalize((root/entry['raw_path']).read_bytes(), source)
    if stored != replay:
        raise ValueError('NORMALIZATION_REPLAY_MISMATCH')
    records = stored['records']
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('DUPLICATE_RECORD_ID')
    # Independently transcribed spot checks from the reviewed table.
    assert records[0]['events'][0]['mass_loss']['value'] == 8.9
    assert records[1]['events'][1]['reported_temperature']['value'] is None
    assert records[9]['activation_energy']['value'] == 133
    assert all(r['vapor_source_status'] == 'UNAVAILABLE' for r in records)
    return dict(files_verified=len(m['files']), bytes_verified=sum(e['bytes'] for e in m['files']),
                sources=len(m['sources']), normalized_study_states=len(records),
                distinct_mineral_groups=stored['distinct_mineral_groups'],
                missing_event_temperatures=stored['missing_event_temperatures'],
                normalization_replay='PASS', physical_validation='NOT_PERFORMED',
                raw_time_series_added=0, new_solver_packages_installed=0)


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
