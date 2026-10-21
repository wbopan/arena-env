import csv
import json
import os

import pytest

WORK = '/root/work'
OUT = os.path.join(WORK, 'cls_report.csv')
HEADER = ['page', 'cls', 'rating', 'shift_count', 'worst_window_start_ms']


def expected():
    by_page = {}
    with open(os.path.join(WORK, 'layout_shifts.jsonl')) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            by_page.setdefault(e['page'], [])
            if not e['hadRecentInput']:
                by_page[e['page']].append((e['startTime'], e['value']))
    res = {}
    for page, es in by_page.items():
        es.sort()
        windows = []
        for i, (t, v) in enumerate(es):
            if windows and t - es[i - 1][0] < 1000 and t - windows[-1]['start'] < 5000:
                windows[-1]['sum'] += v
            else:
                windows.append({'start': t, 'sum': v})
        cls = max(w['sum'] for w in windows)
        starts = [w['start'] for w in windows if w['sum'] >= cls - 1e-9]
        if cls <= 0.1:
            rating = 'good'
        elif cls <= 0.25:
            rating = 'needs-improvement'
        else:
            rating = 'poor'
        res[page] = {'cls': cls, 'rating': rating, 'count': len(es), 'starts': starts}
    return res


@pytest.fixture(scope='module')
def rows():
    assert os.path.isfile(OUT), 'cls_report.csv missing'
    with open(OUT, newline='') as f:
        return list(csv.reader(f))


@pytest.fixture(scope='module')
def exp():
    return expected()


def body(rows):
    return [r for r in rows[1:] if r]


def test_output_exists():
    assert os.path.isfile(OUT)


def test_header_and_pages(rows, exp):
    assert [c.strip() for c in rows[0]] == HEADER
    pages = [r[0] for r in body(rows)]
    assert pages == sorted(exp.keys())


def test_shift_count(rows, exp):
    for r in body(rows):
        assert int(r[3]) == exp[r[0]]['count'], r[0]


def test_cls_values(rows, exp):
    for r in body(rows):
        assert abs(float(r[1]) - exp[r[0]]['cls']) <= 1e-4, r[0]


def test_rating(rows, exp):
    for r in body(rows):
        c = exp[r[0]]['cls']
        if abs(c - 0.1) < 1e-9 or abs(c - 0.25) < 1e-9:
            continue
        assert r[2].strip() == exp[r[0]]['rating'], r[0]


def test_worst_window_start(rows, exp):
    for r in body(rows):
        got = float(r[4])
        assert any(abs(got - s) <= 0.05 for s in exp[r[0]]['starts']), r[0]
