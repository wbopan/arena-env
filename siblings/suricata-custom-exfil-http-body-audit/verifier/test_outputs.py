import json
import re
from pathlib import Path

INPUT = Path('/root/work/requests.jsonl')
OUTPUT = Path('/root/work/qualified.json')


def expected():
    result = []
    for line in INPUT.read_text().splitlines():
        item = json.loads(line)
        head, body = item['request'].split('\r\n\r\n', 1)
        lines = head.split('\r\n')
        method, path, _ = lines[0].split(' ', 2)
        headers = dict(line.split(':', 1) for line in lines[1:])
        modes = [value.strip() for name, value in headers.items() if name.lower() == 'x-tlm-mode']
        fields = dict(part.split('=', 1) for part in body.split('&'))
        blob, sig = fields.get('blob', ''), fields.get('sig', '')
        if (method == 'POST' and path == '/telemetry/v2/report' and 'exfil' in modes
                and re.fullmatch(r'[A-Za-z0-9+/=]{80,}', blob)
                and re.fullmatch(r'[0-9A-Fa-f]{64}', sig)):
            result.append({'id': item['id'], 'blob_chars': len(blob), 'sig_prefix': sig[:8]})
    return sorted(result, key=lambda row: row['id'])


def actual():
    return json.loads(OUTPUT.read_text())


def test_file_exists():
    assert OUTPUT.is_file()


def test_schema_and_order():
    rows = actual()
    assert isinstance(rows, list)
    assert all(set(row) == {'id', 'blob_chars', 'sig_prefix'} for row in rows)
    assert all(type(row['id']) is int and type(row['blob_chars']) is int and type(row['sig_prefix']) is str for row in rows)
    assert [row['id'] for row in rows] == sorted(row['id'] for row in rows)


def test_selected_ids():
    assert [r['id'] for r in actual()] == [r['id'] for r in expected()]


def test_derived_fields():
    assert actual() == expected()
