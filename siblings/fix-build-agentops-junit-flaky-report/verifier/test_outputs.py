import csv
import glob
import xml.etree.ElementTree as ET
from pathlib import Path

WORK = Path('/root/work')
OUT = WORK / 'flaky_report.csv'
HEADER = ['test_id', 'status', 'runs', 'failures', 'fail_rate']


def _expected():
    stats = {}
    for f in sorted(glob.glob(str(WORK / 'runs' / '*.xml'))):
        for tc in ET.parse(f).getroot().iter('testcase'):
            tid = tc.get('classname') + '::' + tc.get('name')
            tags = {c.tag for c in tc}
            s = stats.setdefault(tid, [0, 0])
            if 'failure' in tags or 'error' in tags:
                s[0] += 1
                s[1] += 1
            elif 'skipped' in tags:
                continue
            else:
                s[0] += 1
    rows = []
    for tid, (runs, fails) in stats.items():
        if runs == 0 or fails == 0:
            continue
        status = 'broken' if fails == runs else 'flaky'
        rows.append((tid, status, runs, fails, fails / runs))
    rows.sort(key=lambda r: (0 if r[1] == 'broken' else 1, -r[4], r[0]))
    return rows


def _rows():
    with open(OUT, newline='') as fh:
        return [r for r in csv.reader(fh) if r]


def test_output_exists():
    assert OUT.exists(), 'flaky_report.csv missing'


def test_header():
    assert [h.strip() for h in _rows()[0]] == HEADER


def test_reported_set():
    exp = {r[0] for r in _expected()}
    got = {r[0].strip() for r in _rows()[1:]}
    assert len(_rows()) - 1 == len(exp)
    assert got == exp


def test_status_and_counts():
    exp = {r[0]: r for r in _expected()}
    for r in _rows()[1:]:
        e = exp[r[0].strip()]
        assert r[1].strip() == e[1], r
        assert int(r[2]) == e[2], r
        assert int(r[3]) == e[3], r


def test_fail_rate():
    exp = {r[0]: r for r in _expected()}
    for r in _rows()[1:]:
        assert abs(float(r[4]) - exp[r[0].strip()][4]) <= 1.01e-3, r


def test_order():
    assert [r[0].strip() for r in _rows()[1:]] == [r[0] for r in _expected()]
