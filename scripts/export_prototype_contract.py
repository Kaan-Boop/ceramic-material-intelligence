"""Regenerate reviewed API contract from the application, never edit generated files."""
import json
from pathlib import Path
from apps.api.app.main import app

if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'contracts' / 'prototype-openapi.json'
    target.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)
