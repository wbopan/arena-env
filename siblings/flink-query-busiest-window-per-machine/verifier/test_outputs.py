import csv
import gzip
import json
import os
from collections import defaultdict

WORK = '/root/work'
TASK = os.path.join(WORK, 'data', 'task_events.csv.gz')
OUT = os.path.join(WORK, 'busiest_windows.json')
W = 300_000_000


def _expected():
    win = defaultdict(lambda: defaultdict(list))
    with gzip.open(TASK, 'rt') as f:
        for r in csv.reader(f):
            if not r or r[5] != '1' or r[4].strip() == '':
                continue
            t = int(r[0])
            if t == 0:
                continue
            win[r[4].strip()][(t // W) * W].append(int(r[2]))
    res = {}
    for m, d in win.items():
        best = min(d, key=lambda s: (-len(d[s]), s))
        res[m] = {'window_start': best, 'window_end': best + W,
                  'schedule_count': len(d[best]), 'distinct_jobs': len(set(d[best]))}
    return res


def _load():
    with open(OUT) as f:
        return json.load(f)


def test_output_exists_and_json():
    assert os.path.isfile(OUT)
    assert isinstance(_load(), dict)


def test_machine_set():
    got, exp = _load(), _expected()
    assert set(got) == set(exp), 'missing=%s extra=%s' % (set(exp) - set(got), set(got) - set(exp))


def test_windows():
    got, exp = _load(), _expected()
    for m, e in exp.items():
        g = got[m]
        assert int(g['window_start']) == e['window_start'], m
        assert int(g['window_end']) == e['window_end'], m


def test_counts():
    got, exp = _load(), _expected()
    for m, e in exp.items():
        assert int(got[m]['schedule_count']) == e['schedule_count'], m


def test_distinct_jobs():
    got, exp = _load(), _expected()
    for m, e in exp.items():
        assert int(got[m]['distinct_jobs']) == e['distinct_jobs'], m
