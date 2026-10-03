"""Local-only paginated research adapter; deliberately not a chemistry resolver."""
import sqlite3
import json
from contextlib import closing
from pathlib import Path

DEFAULT_DATABASE = Path(__file__).resolve().parents[1] / 'storage/local-glazy/raw/04_HESAPLAMA_VE_VERI_ARACLARI/ceramic_db.sqlite'
STAGED_DATABASE = Path(__file__).resolve().parents[1] / 'storage/local-glazy/staging/v1.sqlite'

def get_staged_record(source_id, database=STAGED_DATABASE):
    """Retrieve original fields with lineage, never default missing oxides to zero."""
    if type(source_id) is not int or source_id <= 0:
        raise ValueError('Positive integer source ID required')
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        rows = db.execute('SELECT source_line,payload FROM records WHERE source_id=?',(source_id,)).fetchall()
        if len(rows) > 1:
            raise ValueError('Ambiguous duplicate source ID; manual review required')
        if not rows:
            return None
        report = json.loads(db.execute("SELECT value FROM metadata WHERE key='report'").fetchone()[0])
    return {'source_id': source_id, 'source_line': rows[0][0],
            'archive_sha256': report['archive_sha256'], 'parser_version': report['parser_version'],
            'status': 'LOCAL_RESEARCH_QUARANTINE', 'engine_eligible': False,
            'analysis_basis': 'UNKNOWN', 'record': json.loads(rows[0][1])}

def search_recipes(query='', page=1, page_size=20, category='', database=DEFAULT_DATABASE):
    if not isinstance(query, str) or len(query) > 200:
        raise ValueError('Query must be text of at most 200 characters')
    if type(page) is not int or page < 1 or type(page_size) is not int or not 1 <= page_size <= 100:
        raise ValueError('Invalid pagination')
    pattern = '%' + query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
    with closing(sqlite3.connect(Path(database).resolve().as_uri() + '?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA query_only=ON')
        where = " WHERE name LIKE ? ESCAPE '\\'"
        params = [pattern]
        if category == 'CLAY_BODY': where += " AND subtype LIKE 'Clay Body%'"
        elif category == 'GLAZE': where += " AND subtype NOT LIKE 'Clay Body%'"
        elif category == 'ANALYSIS': where, params = " WHERE 0", []
        elif category not in ('', 'RECIPE'): raise ValueError('Unknown archive category')
        total = db.execute('SELECT COUNT(*) FROM recipes' + where, params).fetchone()[0]
        rows = db.execute('SELECT id,name,subtype,cone,surface,ingredients_count FROM recipes' + where
                          + ' ORDER BY name COLLATE NOCASE,id LIMIT ? OFFSET ?',
                          (*params, page_size, (page-1)*page_size)).fetchall()
    return {'scope': 'LOCAL_RESEARCH_QUARANTINE', 'engine_eligible': False,
            'total': total, 'page': page, 'page_size': page_size, 'category': category or 'ALL',
            'items': [dict(row) for row in rows]}
