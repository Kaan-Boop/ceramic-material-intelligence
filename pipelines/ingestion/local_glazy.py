"""Loss-preserving staging of the specific Glazy list export; no chemistry inference."""
import gzip
import json
import sqlite3
from collections import Counter
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
import yaml
from scripts.import_local_glazy import digest

class StrictLoader(yaml.CSafeLoader):
    pass

def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=True)
    return result

StrictLoader.add_constructor('tag:yaml.org,2002:map', mapping)

def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      default=lambda v: v.isoformat() if isinstance(v, (date, datetime)) else str(v))

def blocks(path):
    current, start, size, total = [], 1, 0, 0
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            total += len(line)
            if total > 512_000_000:
                raise ValueError('Expanded archive exceeds 512 MB limit')
            if line.rstrip('\r\n') == '-' and current:
                yield start, ''.join(current)
                current, start, size = [], number, 0
            current.append(line)
            size += len(line)
            if size > 2_000_000:
                raise ValueError('Record exceeds 2 MB limit')
        if current:
            yield start, ''.join(current)

def stage(archive, output, legacy=None):
    archive, output = Path(archive), Path(output)
    if output.exists():
        raise FileExistsError('Choose a new staging filename; existing snapshots are never overwritten')
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {'schema_version': 1, 'parser_version': 'glazy-stage/1',
              'archive_sha256': digest(archive), 'yaml_version': yaml.__version__,
              'status': 'LOCAL_RESEARCH_QUARANTINE', 'engine_eligible': False,
              'received': 0, 'accepted': 0, 'rejected': 0, 'types': {}, 'errors': []}
    types = Counter()
    with closing(sqlite3.connect(output)) as db:
        db.executescript('''
          CREATE TABLE records(seq INTEGER PRIMARY KEY, source_line INTEGER NOT NULL,
            source_id INTEGER NOT NULL, kind TEXT NOT NULL, name TEXT, subtype TEXT,
            payload TEXT NOT NULL, analysis_basis TEXT NOT NULL DEFAULT 'UNKNOWN');
          CREATE TABLE ingredients(record_seq INTEGER, position INTEGER, target_id INTEGER,
            amount REAL, payload TEXT NOT NULL);
          CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
          CREATE INDEX record_identity ON records(source_id);
          CREATE INDEX ingredient_target ON ingredients(target_id);
        ''')
        for seq, (line, block) in enumerate(blocks(archive), 1):
            report['received'] += 1
            try:
                # Aliases are unnecessary in this export and may hide amplification.
                if any(isinstance(t, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken)) for t in yaml.scan(block, Loader=StrictLoader)):
                    raise ValueError('YAML aliases/anchors not accepted')
                obj = yaml.load(block, Loader=StrictLoader)
                if not isinstance(obj, list) or len(obj) != 1 or not isinstance(obj[0], dict):
                    raise ValueError('Expected one mapping per top-level block')
                row = obj[0]
                if type(row.get('ID')) is not int or row['ID'] <= 0 or not isinstance(row.get('Type'), str):
                    raise ValueError('Invalid ID or Type')
                payload = encode(row)
                ingredients = row.get('Ingredients', [])
                if not isinstance(ingredients, list) or any(not isinstance(i, dict) for i in ingredients):
                    raise ValueError('Invalid Ingredients structure')
                prepared = []
                for position, ing in enumerate(ingredients):
                    target = ing.get('ID')
                    amount = ing.get('Percentage')
                    prepared.append((seq, position, target if type(target) is int else None,
                                     amount if type(amount) in (int, float) else None, encode(ing)))
                db.execute('INSERT INTO records(seq,source_line,source_id,kind,name,subtype,payload) VALUES (?,?,?,?,?,?,?)',
                           (seq,line,row['ID'],row['Type'],row.get('Name'),row.get('Subtype'),payload))
                db.executemany('INSERT INTO ingredients VALUES (?,?,?,?,?)', prepared)
                types[row['Type']] += 1
                report['accepted'] += 1
            except (yaml.YAMLError, ValueError, TypeError) as exc:
                report['rejected'] += 1
                report['errors'].append({'sequence': seq, 'line': line, 'reason': str(exc)[:400]})
        report['types'] = dict(types)
        queries = {
          'duplicate_source_ids': 'SELECT COUNT(*) FROM (SELECT source_id FROM records GROUP BY source_id HAVING COUNT(*)>1)',
          'ingredient_rows': 'SELECT COUNT(*) FROM ingredients',
          'unresolved_target_rows': 'SELECT COUNT(*) FROM ingredients i WHERE NOT EXISTS(SELECT 1 FROM records r WHERE r.source_id=i.target_id)',
          'recipe_target_rows': "SELECT COUNT(*) FROM ingredients i WHERE EXISTS(SELECT 1 FROM records r WHERE r.source_id=i.target_id AND r.kind='Recipe')",
          'missing_or_negative_amounts': 'SELECT COUNT(*) FROM ingredients WHERE amount IS NULL OR amount<0',
          'records_with_percent_analysis': "SELECT COUNT(*) FROM records WHERE json_type(payload,'$.\"Percent Analysis\"')='object'",
          'clay_body_recipes': "SELECT COUNT(*) FROM records WHERE kind='Recipe' AND subtype LIKE 'Clay Body%'",
        }
        report['checks'] = {key:{'sql':sql,'value':db.execute(sql).fetchone()[0]} for key,sql in queries.items()}
        if legacy:
            with closing(sqlite3.connect(Path(legacy).resolve().as_uri()+'?mode=ro', uri=True)) as old:
                report['legacy_comparison'] = {}
                for kind, table in [('Recipe','recipes'),('Material','materials')]:
                    old_ids = {r[0] for r in old.execute('SELECT id FROM '+table)}
                    new_ids = {r[0] for r in db.execute('SELECT source_id FROM records WHERE kind=?',(kind,))}
                    report['legacy_comparison'][kind] = {'only_in_raw':sorted(new_ids-old_ids), 'only_in_legacy':sorted(old_ids-new_ids)}
        db.execute('INSERT INTO metadata VALUES (?,?)', ('report',encode(report)))
        db.commit()
    output.with_suffix('.report.json').write_text(encode(report),encoding='utf-8')
    return report

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--legacy',type=Path)
    a=p.parse_args()
    print(encode(stage(a.archive,a.output,a.legacy)))
