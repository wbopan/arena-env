import json
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.spatial.distance import cdist

WORK = Path("/root/work")
OUT = WORK / "image_scores.json"
EPS, MS, W = 10.0, 4, 1.4
TOL = 2e-3


def cluster_centroids(P):
    n = len(P)
    if n == 0:
        return np.zeros((0, 2))
    S = P * np.array([W, 2 - W])
    D = cdist(S, S)
    adj = D <= EPS
    core = adj.sum(axis=1) >= MS
    lab = np.full(n, -1)
    nxt = 0
    for s in range(n):
        if not core[s] or lab[s] >= 0:
            continue
        q = deque([s])
        lab[s] = nxt
        while q:
            u = q.popleft()
            for v in np.flatnonzero(adj[u] & core):
                if lab[v] < 0:
                    lab[v] = nxt
                    q.append(v)
        nxt += 1
    final = lab.copy()
    core_idx = np.flatnonzero(core)
    for i in range(n):
        if core[i] or len(core_idx) == 0:
            continue
        dd = D[i, core_idx]
        j = int(np.argmin(dd))
        if dd[j] <= EPS:
            final[i] = lab[core_idx[j]]
    return np.array([P[final == c].mean(axis=0) for c in range(nxt)]).reshape(-1, 2)


def compute_expected():
    cit = pd.read_csv(WORK / "citsci.csv")
    ex = pd.read_csv(WORK / "expert.csv")
    res = {}
    for name, g in ex.groupby("file_rad"):
        E = g[["x", "y"]].to_numpy(float)
        P = cit.loc[cit.file_rad == name, ["x", "y"]].to_numpy(float)
        C = cluster_centroids(P)
        d = []
        if len(C):
            M = cdist(C, E)
            flat = sorted((M[a, b], a, b) for a in range(len(C)) for b in range(len(E)))
            ua, ub = set(), set()
            for dist, a, b in flat:
                if dist > 100:
                    break
                if a in ua or b in ub:
                    continue
                ua.add(a)
                ub.add(b)
                d.append(dist)
        m = len(d)
        res[name] = {
            "n_clusters": len(C),
            "n_matched": m,
            "F1": (2 * m / (len(C) + len(E))) if m else 0.0,
            "delta": float(np.mean(d)) if m else None,
        }
    return res


@pytest.fixture(scope="module")
def expected():
    return compute_expected()


@pytest.fixture(scope="module")
def agent():
    assert OUT.exists(), f"missing {OUT}"
    with open(OUT) as f:
        return json.load(f)


def test_file_exists():
    assert OUT.exists()


def test_schema(agent, expected):
    assert "images" in agent and "mean_F1" in agent and "mean_delta" in agent
    assert set(agent["images"].keys()) == set(expected.keys())
    for name, rec in agent["images"].items():
        for k in ("n_clusters", "n_matched", "F1", "delta"):
            assert k in rec, f"{name} missing {k}"


def test_counts(agent, expected):
    for name, e in expected.items():
        a = agent["images"][name]
        assert int(a["n_clusters"]) == e["n_clusters"], f"{name} n_clusters {a['n_clusters']} != {e['n_clusters']}"
        assert int(a["n_matched"]) == e["n_matched"], f"{name} n_matched {a['n_matched']} != {e['n_matched']}"


def test_per_image_scores(agent, expected):
    for name, e in expected.items():
        a = agent["images"][name]
        assert abs(float(a["F1"]) - e["F1"]) <= TOL, f"{name} F1"
        if e["delta"] is None:
            assert a["delta"] is None, f"{name} delta should be null"
        else:
            assert a["delta"] is not None and abs(float(a["delta"]) - e["delta"]) <= TOL, f"{name} delta"


def test_means(agent, expected):
    f1 = np.mean([e["F1"] for e in expected.values()])
    dl = np.mean([e["delta"] for e in expected.values() if e["delta"] is not None])
    assert abs(float(agent["mean_F1"]) - f1) <= TOL
    assert abs(float(agent["mean_delta"]) - dl) <= TOL
