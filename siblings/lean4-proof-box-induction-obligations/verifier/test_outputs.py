import json
from pathlib import Path

ROOT = Path('/root/work')


def expected():
    result = []
    for row in json.loads((ROOT / 'recurrences.json').read_text()):
        lo_x, hi_x, lo_y, hi_y = row['box']
        def inside(x, y):
            return lo_x <= x <= hi_x and lo_y <= y <= hi_y
        bad = None
        for x in (lo_x, hi_x):
            for y in (lo_y, hi_y):
                nx = row['a'] * x + row['b'] * y + row['c']
                ny = row['d'] * x + row['e'] * y + row['f']
                if not inside(nx, ny) and bad is None:
                    bad = [x, y]
        base = inside(*row['start'])
        result.append({'id': row['id'], 'base_ok': base,
                       'step_ok': bad is None,
                       'induction_ready': base and bad is None,
                       'witness': bad})
    return result


def output():
    return json.loads((ROOT / 'obligations.json').read_text())


def test_file_exists():
    assert (ROOT / 'obligations.json').is_file()


def test_schema():
    rows = output()
    assert isinstance(rows, list) and len(rows) == len(expected())
    for row in rows:
        assert isinstance(row, dict)
        assert set(row) == {'id', 'base_ok', 'step_ok', 'induction_ready', 'witness'}
        assert isinstance(row['id'], str)
        assert all(type(row[k]) is bool for k in ('base_ok', 'step_ok', 'induction_ready'))
        assert row['witness'] is None or (isinstance(row['witness'], list)
            and len(row['witness']) == 2 and all(type(v) is int for v in row['witness']))


def test_base_obligations():
    assert [(r['id'], r['base_ok']) for r in output()] == [(r['id'], r['base_ok']) for r in expected()]


def test_step_obligations_and_witnesses():
    assert [(r['step_ok'], r['witness']) for r in output()] == [(r['step_ok'], r['witness']) for r in expected()]


def test_combined_obligations():
    assert [r['induction_ready'] for r in output()] == [r['induction_ready'] for r in expected()]
