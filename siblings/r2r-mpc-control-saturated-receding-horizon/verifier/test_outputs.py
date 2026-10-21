import csv
import json
import os

import numpy as np
import pytest

W = "/root/work"
OUT = os.path.join(W, "closed_loop.csv")


def expected():
    A = np.loadtxt(os.path.join(W, "A.csv"), delimiter=",")
    B = np.loadtxt(os.path.join(W, "B.csv"), delimiter=",")
    with open(os.path.join(W, "mpc_config.json")) as f:
        c = json.load(f)
    Q = np.diag(c["Q_diag"])
    R = np.diag(c["R_diag"])

    P = Q.copy()
    K = None
    for _ in range(c["horizon_N"]):
        K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
        P = Q + A.T @ P @ (A - B @ K)

    x = np.array(c["x0"], float)
    norms, us = [], []
    for _ in range(c["steps"]):
        u = np.clip(-K @ x, -c["u_max"], c["u_max"])
        norms.append(np.linalg.norm(x))
        us.append(u)
        x = A @ x + B @ u
    return c, np.array(norms), np.array(us)


@pytest.fixture(scope="module")
def rows():
    assert os.path.exists(OUT), "closed_loop.csv missing"
    with open(OUT) as f:
        r = list(csv.reader(f))
    return r


def test_header(rows):
    assert [h.strip() for h in rows[0]] == ["k", "x_norm", "u1", "u2", "u3"]


def test_row_count_and_k(rows):
    c, _, _ = expected()
    data = [r for r in rows[1:] if r]
    assert len(data) == c["steps"]
    assert [int(float(r[0])) for r in data] == list(range(c["steps"]))


def test_x_norm(rows):
    _, norms, _ = expected()
    got = np.array([float(r[1]) for r in rows[1:] if r])
    assert np.allclose(got, norms, rtol=1e-4, atol=1e-4)


def test_inputs(rows):
    _, _, us = expected()
    got = np.array([[float(v) for v in r[2:5]] for r in rows[1:] if r])
    assert got.shape == us.shape
    assert np.allclose(got, us, rtol=1e-4, atol=1e-4)


def test_saturation_respected(rows):
    c, _, _ = expected()
    got = np.array([[float(v) for v in r[2:5]] for r in rows[1:] if r])
    assert np.all(np.abs(got) <= c["u_max"] + 1e-6)
