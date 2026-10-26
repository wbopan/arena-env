import csv
import json
import re
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'audit.json'


def inputs():
    with (ROOT / 'uapi_commands.csv').open(newline='') as f:
        authoritative = {r['name']: r['direction'] for r in csv.DictReader(f)}
    text = (ROOT / 'dev_audit.txt').read_text()
    found = re.findall(r'^ioctl\$([A-Z0-9_]+)\(fd fd_ppdev, cmd const\[\1\], arg ptr\[(in|out|inout), int32\]\)$', text, re.M)
    described = dict(found)
    constants = set()
    for line in (ROOT / 'dev_audit.txt.const').read_text().splitlines():
        match = re.fullmatch(r'\s*([A-Z][A-Z0-9_]*)\s*=\s*\d+\s*', line)
        if match:
            constants.add(match.group(1))
    return authoritative, described, constants


def output():
    return json.loads(OUT.read_text())


def test_file_exists():
    assert OUT.is_file()


def test_json_schema():
    result = output()
    assert isinstance(result, dict) and set(result) == {'missing_constants', 'unused_constants', 'direction_mismatches'}
    assert all(isinstance(result[k], list) for k in result)
    assert all(isinstance(x, str) for k in ('missing_constants', 'unused_constants') for x in result[k])
    assert all(isinstance(x, dict) and set(x) == {'name', 'expected', 'actual'} for x in result['direction_mismatches'])


def test_constant_audit():
    _, described, constants = inputs()
    result = output()
    assert result['missing_constants'] == sorted(described.keys() - constants)
    assert result['unused_constants'] == sorted(constants - described.keys())


def test_pointer_directions():
    authoritative, described, _ = inputs()
    expected = [dict(name=n, expected=authoritative[n], actual=d) for n, d in described.items() if d != authoritative[n]]
    assert output()['direction_mismatches'] == sorted(expected, key=lambda entry: entry['name'])
