import csv
import gzip
import os
from collections import defaultdict

WORK = '/root/work'
TASK = os.path.join(WORK, 'data', 'task_events.csv.gz')
JOB = os.path.join(WORK, 'data', 'job_events.csv.gz')
OUT = os.path.join(WORK, 'stages.csv')
GAP = 600_000_000


def _expected():
    finished = set()
    with gzip.open(JOB, 'rt') as f:
        for row in csv.reader(f):
            if row and int(row[3]) == 4:
                finished.add(int(row[2]))
    subs = defaultdict(list)
    with gzip.open(TASK, 'rt') as f:
        for row in csv.reader(f):
            if row and int(row[5]) == 0:
                subs[int(row[2])].append(int(row[0]))
    res = {}
    for jid, ts in subs.items():
        if jid not in finished:
            continue
        ts.sort()
        sizes = [1]
        for a, b in zip(ts, ts[1:]):
            if b - a >= GAP:
                sizes.append(1)
            else:
                sizes[-1] += 1
        res[jid] = (len(sizes), max(sizes))
    return res


def _rows():
    with open(OUT, newline='') as f:
        return [r for r in csv.reader(f) if r]


def test_output_exists():
    assert os.path.isfile(OUT), 'stages.csv missing'


def test_header():
    rows = _rows()
    assert [c.strip() for c in rows[0]] == ['job_id', 'num_stages', 'largest_stage']


def test_job_set():
    exp = _expected()
    ids = [int(r[0]) for r in _rows()[1:]]
    assert len(ids) == len(set(ids)), 'duplicate job rows'
    assert set(ids) == set(exp), 'missing=%s extra=%s' % (set(exp) - set(ids), set(ids) - set(exp))


def test_sorted():
    ids = [int(r[0]) for r in _rows()[1:]]
    assert ids == sorted(ids)


def test_values():
    exp = _expected()
    bad = []
    for r in _rows()[1:]:
        jid = int(r[0])
        got = (int(r[1]), int(r[2]))
        if exp.get(jid) != got:
            bad.append((jid, got, exp.get(jid)))
    assert not bad, 'mismatches (job, got, expected): %s' % bad[:5]
