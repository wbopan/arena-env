import json
import re
from pathlib import Path

WORK = Path('/root/work')
OUT = WORK / 'ci_summary.json'


def _entries():
    body = []
    for line in (WORK / 'ci_log.txt').read_text().splitlines():
        parts = line.split(' ', 1)
        body.append(parts[1] if len(parts) > 1 else '')
    start = next(i for i, s in enumerate(body) if 'short test summary info' in s)
    out = []
    for s in body[start + 1:]:
        if s.startswith('='):
            break
        if s.startswith('FAILED ') or s.startswith('ERROR '):
            kind, rest = s.split(' ', 1)
            nodeid, exc = rest.split(' - ', 1)
            out.append((kind, nodeid, exc))
    return out


def _expected():
    ents = _entries()
    by = {}
    mods = set()
    files = {}
    for kind, nodeid, exc in ents:
        et = exc.split(':', 1)[0].strip()
        by[et] = by.get(et, 0) + 1
        if et == 'ModuleNotFoundError':
            m = re.search(r"No module named '([^']+)'", exc)
            if m:
                mods.add(m.group(1).split('.')[0])
        f = nodeid.split('::', 1)[0]
        files[f] = files.get(f, 0) + 1
    worst = sorted(files.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return {
        'failed': sum(1 for e in ents if e[0] == 'FAILED'),
        'errors': sum(1 for e in ents if e[0] == 'ERROR'),
        'by_exception': by,
        'missing_modules': sorted(mods),
        'worst_file': worst,
    }


def _load():
    return json.loads(OUT.read_text())


def test_output_exists_and_valid_json():
    assert OUT.exists(), 'ci_summary.json missing'
    assert isinstance(_load(), dict)


def test_schema():
    d = _load()
    assert set(d.keys()) == {'failed', 'errors', 'by_exception', 'missing_modules', 'worst_file'}
    assert isinstance(d['failed'], int) and isinstance(d['errors'], int)
    assert isinstance(d['by_exception'], dict)
    assert isinstance(d['missing_modules'], list)
    assert isinstance(d['worst_file'], str)


def test_counts():
    d, e = _load(), _expected()
    assert d['failed'] == e['failed']
    assert d['errors'] == e['errors']


def test_by_exception():
    d, e = _load(), _expected()
    assert {k: int(v) for k, v in d['by_exception'].items()} == e['by_exception']


def test_missing_modules():
    assert _load()['missing_modules'] == _expected()['missing_modules']


def test_worst_file():
    assert _load()['worst_file'] == _expected()['worst_file']
