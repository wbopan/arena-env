import json
import os

import numpy as np
import pytest

W = "/root/work"
OUT = os.path.join(W, "linearization.json")


def expected():
    with open(os.path.join(W, "system_config.json")) as f:
        c = json.load(f)
    n = c["n_sections"]
    EA, R, fb, dt = c["EA"], c["R"], c["fb"], c["dt"]
    L, J, T = c["L"], c["J"], c["T_ref"]

    v = np.zeros(n)
    vp, Tp = c["v0"], 0.0
    for i in range(n):
        v[i] = vp * (EA - Tp) / (EA - T[i])
        vp, Tp = v[i], T[i]

    u = np.zeros(n)
    for i in range(n):
        Tn = T[i + 1] if i < n - 1 else 0.0
        u[i] = (fb * v[i] - R ** 2 * (Tn - T[i])) / R

    Ac = np.zeros((2 * n, 2 * n))
    Bc = np.zeros((2 * n, n))
    for i in range(n):
        Ac[i, i] = -v[i] / L[i]
        Ac[i, n + i] = (EA - T[i]) / L[i]
        if i > 0:
            Ac[i, i - 1] = v[i - 1] / L[i]
            Ac[i, n + i - 1] = (T[i - 1] - EA) / L[i]
        Ac[n + i, i] = -R ** 2 / J[i]
        Ac[n + i, n + i] = -fb / J[i]
        if i < n - 1:
            Ac[n + i, i + 1] = R ** 2 / J[i]
        Bc[n + i, i] = R / J[i]

    A = np.eye(2 * n) + dt * Ac
    B = dt * Bc
    rho = float(np.max(np.abs(np.linalg.eigvals(A))))
    return n, v, u, A, B, rho


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "linearization.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_schema(out):
    n = expected()[0]
    for k in ["v_ref", "u_ref", "A_matrix", "B_matrix", "spectral_radius"]:
        assert k in out, f"missing {k}"
    assert np.array(out["A_matrix"], dtype=float).shape == (2 * n, 2 * n)
    assert np.array(out["B_matrix"], dtype=float).shape == (2 * n, n)
    assert len(out["v_ref"]) == n and len(out["u_ref"]) == n


def test_steady_state(out):
    _, v, u, _, _, _ = expected()
    assert np.allclose(np.array(out["v_ref"], float), v, rtol=1e-6, atol=1e-9)
    assert np.allclose(np.array(out["u_ref"], float), u, rtol=1e-6, atol=1e-9)


def test_A_matrix(out):
    A = expected()[3]
    assert np.allclose(np.array(out["A_matrix"], float), A, rtol=1e-6, atol=1e-9)


def test_B_matrix(out):
    B = expected()[4]
    assert np.allclose(np.array(out["B_matrix"], float), B, rtol=1e-6, atol=1e-9)


def test_spectral_radius(out):
    rho = expected()[5]
    assert abs(float(out["spectral_radius"]) - rho) <= 1e-6 * max(1.0, rho)
