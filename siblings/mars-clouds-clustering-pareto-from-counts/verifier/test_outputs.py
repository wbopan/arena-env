from pathlib import Path

import numpy as np
import pandas as pd
import pytest

WORK = Path("/root/work")
OUT = WORK / "pareto.csv"
COLS = ["F1", "delta", "min_samples", "epsilon", "shape_weight"]
TOL = 1e-4


def compute_expected():
    df = pd.read_csv(WORK / "grid_counts.csv")
    stats = []
    for key, g in df.groupby(["min_samples", "epsilon", "shape_weight"]):
        f1, dl = [], []
        for r in g.itertuples(index=False):
            if r.n_matched > 0:
                f1.append(2 * r.n_matched / (r.n_clusters + r.n_expert))
                dl.append(r.sum_dist / r.n_matched)
            else:
                f1.append(0.0)
        F = float(np.mean(f1))
        if F > 0.5 and dl:
            stats.append((F, float(np.mean(dl)), int(key[0]), int(key[1]), round(float(key[2]), 1)))
    front = []
    for p in stats:
        dom = any(q[0] >= p[0] and q[1] <= p[1] and (q[0] > p[0] or q[1] < p[1]) for q in stats)
        if not dom:
            front.append(p)
    front.sort(key=lambda t: (-t[0], t[1]))
    return front


@pytest.fixture(scope="module")
def expected():
    return compute_expected()


@pytest.fixture(scope="module")
def agent():
    assert OUT.exists(), f"missing {OUT}"
    return pd.read_csv(OUT)


def test_file_exists():
    assert OUT.exists()


def test_columns(agent):
    assert list(agent.columns) == COLS
    assert len(agent) > 0


def test_configurations_match(agent, expected):
    got = {(int(r.min_samples), int(r.epsilon), round(float(r.shape_weight), 1)) for r in agent.itertuples()}
    exp = {(p[2], p[3], p[4]) for p in expected}
    assert got == exp, f"extra={got - exp}, missing={exp - got}"
    assert len(agent) == len(expected)


def test_values(agent, expected):
    lookup = {(int(r.min_samples), int(r.epsilon), round(float(r.shape_weight), 1)): r for r in agent.itertuples()}
    for p in expected:
        r = lookup[(p[2], p[3], p[4])]
        assert abs(float(r.F1) - p[0]) <= TOL, f"F1 for {p[2:]}"
        assert abs(float(r.delta) - p[1]) <= TOL, f"delta for {p[2:]}"


def test_sorted_by_f1_desc(agent):
    f = agent["F1"].to_numpy(float)
    assert np.all(np.diff(f) <= 1e-12), "rows must be sorted by F1 descending"
