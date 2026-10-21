import csv
import json
import os

import numpy as np
import pytest

WORK = "/root/work"
OUT = os.path.join(WORK, "branch_flows.csv")
NET = os.path.join(WORK, "network.json")
TOL = 0.05


def compute_expected():
    with open(NET) as f:
        d = json.load(f)
    base = float(d["baseMVA"])
    buses = d["bus"]
    pos = {int(b[0]): i for i, b in enumerate(buses)}
    n = len(buses)
    inj = np.array([-float(b[2]) for b in buses])
    for g in d["gen"]:
        if int(g[7]) == 1:
            inj[pos[int(g[0])]] += float(g[1])
    lines = [b for b in d["branch"] if int(b[10]) == 1]
    B = np.zeros((n, n))
    for b in lines:
        i, j = pos[int(b[0])], pos[int(b[1])]
        y = 1.0 / float(b[3])
        B[i, i] += y
        B[j, j] += y
        B[i, j] -= y
        B[j, i] -= y
    ref = [i for i, b in enumerate(buses) if int(b[1]) == 3][0]
    keep = [i for i in range(n) if i != ref]
    theta = np.zeros(n)
    theta[keep] = np.linalg.solve(B[np.ix_(keep, keep)], inj[keep] / base)
    rows = []
    for b in lines:
        i, j = pos[int(b[0])], pos[int(b[1])]
        flow = (theta[i] - theta[j]) / float(b[3]) * base
        rows.append((int(b[0]), int(b[1]), flow, abs(flow) / float(b[5]) * 100.0))
    return rows


@pytest.fixture(scope="module")
def expected():
    return compute_expected()


@pytest.fixture(scope="module")
def agent():
    assert os.path.exists(OUT), "branch_flows.csv missing"
    with open(OUT, newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    return fields, rows


def test_output_exists():
    assert os.path.exists(OUT)


def test_header(agent):
    fields, _ = agent
    assert [c.strip() for c in fields] == ["from_bus", "to_bus", "flow_MW", "loading_pct"]


def test_branch_set_and_order(agent, expected):
    _, rows = agent
    assert len(rows) == len(expected)
    for r, e in zip(rows, expected):
        assert int(float(r["from_bus"])) == e[0]
        assert int(float(r["to_bus"])) == e[1]


def test_flows(agent, expected):
    _, rows = agent
    assert len(rows) == len(expected)
    for r, e in zip(rows, expected):
        assert abs(float(r["flow_MW"]) - e[2]) <= TOL, (r, e)


def test_loading(agent, expected):
    _, rows = agent
    assert len(rows) == len(expected)
    for r, e in zip(rows, expected):
        assert abs(float(r["loading_pct"]) - e[3]) <= TOL, (r, e)
