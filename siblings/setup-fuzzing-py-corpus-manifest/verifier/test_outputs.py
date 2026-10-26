import csv
import hashlib
import json
from pathlib import Path

ROOT = Path('/root/work')
OUTPUT = ROOT / 'seed_manifest.tsv'


def selections():
    unique = {}
    for file in (ROOT / 'seeds').iterdir():
        raw = file.read_bytes()
        try:
            decoded = raw.decode('utf-8')
        except UnicodeDecodeError:
            category, key = 'binary', raw
        else:
            try:
                value = json.loads(decoded)
            except json.JSONDecodeError:
                category, key = 'text', raw
            else:
                category = 'json'
                key = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        candidate = (len(raw), file.name, raw)
        old = unique.get((category, key))
        if old is None or candidate[:2] < old[:2]:
            unique[(category, key)] = candidate
    result = []
    for category in ('json', 'text', 'binary'):
        for length, name, raw in sorted((value for (kind, _), value in unique.items() if kind == category), key=lambda v: v[:2])[:2]:
            result.append({'category': category, 'filename': name, 'bytes': str(length), 'sha256': hashlib.sha256(raw).hexdigest()})
    return result


def read():
    with OUTPUT.open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        return reader.fieldnames, list(reader)


def test_file_exists():
    assert OUTPUT.is_file()


def test_header_and_row_count():
    header, rows = read()
    assert header == ['category', 'filename', 'bytes', 'sha256']
    assert len(rows) == len(selections())


def test_selected_names_and_order():
    _, rows = read()
    assert [(r['category'], r['filename']) for r in rows] == [(r['category'], r['filename']) for r in selections()]


def test_lengths_and_hashes():
    _, rows = read()
    assert [(r['bytes'], r['sha256']) for r in rows] == [(r['bytes'], r['sha256']) for r in selections()]
