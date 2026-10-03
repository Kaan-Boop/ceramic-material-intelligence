"""Preserve a user-supplied archive. Never execute its code or promote chemistry."""
import argparse
import hashlib
import json
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path('01_SIR_RECETELERI_VERITABANI/Acik_Kaynak_Glazy_Veri_Seti')
FILES = [ARCHIVE / n for n in ('glazy_latest.yaml.gz', 'featured_glaze_recipes.json',
         'featured_glaze_recipes.csv', 'ceramic_materials_index.json')]
FILES += [Path('04_HESAPLAMA_VE_VERI_ARACLARI') / n for n in
          ('ceramic_db.sqlite', 'download_and_process_glazy.py')]

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def profile(path):
    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        db.execute('PRAGMA query_only=ON')
        queries = {
            'recipes': 'SELECT COUNT(*) FROM recipes',
            'materials': 'SELECT COUNT(*) FROM materials',
            'ingredient_rows': 'SELECT COUNT(*) FROM recipe_ingredients',
            'orphan_recipe_links': 'SELECT COUNT(*) FROM recipe_ingredients i LEFT JOIN recipes r ON r.id=i.recipe_id WHERE r.id IS NULL',
            'unresolved_material_links': 'SELECT COUNT(*) FROM recipe_ingredients i LEFT JOIN materials m ON m.id=i.material_id WHERE m.id IS NULL',
            'missing_or_negative_amounts': 'SELECT COUNT(*) FROM recipe_ingredients WHERE percentage IS NULL OR percentage < 0',
            'recipes_without_ingredients': 'SELECT COUNT(*) FROM recipes r WHERE NOT EXISTS (SELECT 1 FROM recipe_ingredients i WHERE i.recipe_id=r.id)',
            'zero_or_missing_silica': 'SELECT COUNT(*) FROM recipes WHERE sio2 IS NULL OR sio2=0',
        }
        return {'integrity_check': db.execute('PRAGMA integrity_check').fetchone()[0],
                'checks': {key: {'value': db.execute(sql).fetchone()[0], 'sql': sql}
                           for key, sql in queries.items()}}

def ingest(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents:
        raise ValueError('Destination must be separate from source')
    entries = []
    # Preflight before copying; an existing different file is never overwritten.
    for relative in FILES:
        original, target = source / relative, destination / 'raw' / relative
        checksum = digest(original)
        if target.exists() and digest(target) != checksum:
            raise ValueError(f'Existing snapshot differs: {target}')
        entries.append({'relative_path': relative.as_posix(), 'sha256': checksum,
                        'bytes': original.stat().st_size})
    for entry in entries:
        relative = Path(entry['relative_path'])
        target = destination / 'raw' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source / relative, target)
        if digest(target) != entry['sha256']:
            raise ValueError(f'Copy verification failed: {target}')
    report = {
        'schema_version': 1, 'source_name': 'User-supplied Antigravity / Glazy archive',
        'upstream_url': 'https://github.com/derekphilipau/glazy-data',
        'upstream_commit': None, 'upstream_download_date': None,
        'imported_at': datetime.now(timezone.utc).isoformat(),
        'source_directory': str(source), 'files': entries,
        'scope': 'LOCAL_RESEARCH_QUARANTINE', 'engine_eligible': False,
        'publication_allowed': False, 'training_allowed': False,
        'license': 'RECORD_LEVEL_REVIEW_REQUIRED',
        'limitations': [
            'Existing SQLite is a derived index, not a lossless source.',
            'Legacy importer replaces missing chemistry with zero.',
            'Legacy SiO2/Al2O3 field is a mass ratio, not UMF or atomic Si/Al.',
            'Legacy importer suppresses parse errors; raw reconciliation is pending.',
            'Archive identity does not establish record-level reuse permission.',
        ],
        'profile': profile(destination / 'raw' / FILES[-2]),
    }
    (destination / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=ROOT / 'storage/local-glazy')
    args = parser.parse_args()
    print(json.dumps(ingest(args.source, args.destination), ensure_ascii=True, indent=2))
