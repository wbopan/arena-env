import csv
import json
import os

import numpy as np
import pytest

WORK = '/root/work'
OUT = os.path.join(WORK, 'branch_flows.csv')
NET = os.path.join(WORK, 'network.json')
TOL = 0.05


def expected_rows():
    with open(NET) as f:
        d = json.load(f)
    base = float(d['baseMVA'])
    bus = d['bus']
    idx = {int(b[0]): i for i, b in enumerate(bus)}
    n = len(bus)
    p = np.array([-float(b[2]) for b in bus])
    for g in d['gen']:
        if int(g[7]) == 1:
            p[idx[int(g[0])]] += float(g[1])
    p = p / base
    B = np.zeros((n, n))
    live = [br for br in d['branch'] if int(br[10]) == 1]
    for br in live:
        f, t = idx[int(br[0])], idx[int(br[1])]
        b = 1.0 / float(br[3])
        B[f, f] += b
        B[t, t] += b
        B[f, t] -= b
        B[t, f] -= b
    s = next(i for i, b in enumerate(bus) if int(b[1]) == 3)
    keep = [i for i in range(n) if i != s]
    theta = np.zeros(n)
    theta[keep] = np.linalg.solve(B[np.ix_(keep, keep)], p[keep])
    rows = []
    for br in live:
        f, t = idx[int(br[0])], idx[int(br[1])]
        flow = (theta[f] - theta[t]) / float(br[3]) * base
        rows.append((int(br[0]), int(br[1]), flow, abs(flow) / float(br[5]) * 100.0))
    return rows


@pytest.fixture(scope='module')
def agent_rows():
    assert os.path.exists(OUT), 'branch_flows.csv missing'
    with open(OUT, newline='') as f:
        return [r for r in csv.reader(f) if r]


@pytest.fixture(scope='module')
def exp():
    return expected_rows()


def test_file_exists():
    assert os.path.exists(OUT)


def test_header(agent_rows):
    assert [c.strip() for c in agent_rows[0]] == ['from_bus', 'to_bus', 'flow_MW', 'loading_pct']


def test_branch_rows(agent_rows, exp):
    body = agent_rows[1:]
    assert len(body) == len(exp)
    for r, e in zip(body, exp):
        assert int(float(r[0])) == e[0] and int(float(r[1])) == e[1]


def test_flows(agent_rows, exp):
    body = agent_rows[1:]
    assert len(body) == len(exp)
    for r, e in zip(body, exp):
        assert abs(float(r[2]) - e[2]) <= TOL, (r, e)


def test_loading(agent_rows, exp):
    body = agent_rows[1:]
    assert len(body) == len(exp)
    for r, e in zip(body, exp):
        assert abs(float(r[3]) - e[3]) <= TOL, (r, e)
