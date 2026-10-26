#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_corpus.py <<'PY'
import csv
import hashlib
import json
from pathlib import Path

base = Path('/root/work')
representatives = {}
for path in (base / 'seeds').iterdir():
    data = path.read_bytes()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        kind, signature = 'binary', data
    else:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            kind, signature = 'text', data
        else:
            kind = 'json'
            signature = json.dumps(parsed, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    key = kind, signature
    if key not in representatives or (len(data), path.name) < (len(representatives[key][1]), representatives[key][0].name):
        representatives[key] = (path, data)
with (base / 'seed_manifest.tsv').open('w', encoding='utf-8', newline='') as stream:
    writer = csv.writer(stream, delimiter='\t')
    writer.writerow(['category', 'filename', 'bytes', 'sha256'])
    for kind in ('json', 'text', 'binary'):
        choices = sorted((pair for (category, _), pair in representatives.items() if category == kind), key=lambda pair: (len(pair[1]), pair[0].name))
        for path, data in choices[:2]:
            writer.writerow([kind, path.name, len(data), hashlib.sha256(data).hexdigest()])
PY
python3 /tmp/solve_corpus.py
