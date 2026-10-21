import csv
import os

import numpy as np
import pytest

W = "/root/work"
OUT = os.path.join(W, "lead_lag.csv")
LAGS = list(range(-6, 7))


def hp_cycle(y, lam):
    T = len(y)
    D = np.zeros((T - 2, T))
    for i in range(T - 2):
        D[i, i], D[i, i + 1], D[i, i + 2] = 1.0, -2.0, 1.0
    return y - np.linalg.solve(np.eye(T) + lam * D.T @ D, y)


def lagcorr(a, b, k):
    T = len(a)
    if k >= 0:
        x, y = a[:T - k], b[k:]
    else:
        x, y = a[-k:], b[:T + k]
    return float(np.corrcoef(x, y)[0, 1])


@pytest.fixture(scope="module")
def expected():
    with open(os.path.join(W, "indicators.csv")) as f:
        rows = sorted(csv.DictReader(f), key=lambda r: r["month"])
    ip = hp_cycle(np.log([float(r["ip_index"]) for r in rows]), 14400)
    pay = hp_cycle(np.log([float(r["payroll_thousands"]) for r in rows]), 14400)
    ur = hp_cycle(np.array([float(r["unemployment_rate"]) for r in rows]), 14400)
    return {k: (lagcorr(ip, pay, k), lagcorr(ip, ur, k)) for k in LAGS}


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "lead_lag.csv missing"
    with open(OUT) as f:
        r = list(csv.reader(f))
    return r


def test_file_exists():
    assert os.path.exists(OUT)


def test_header_and_lags(out):
    assert [h.strip() for h in out[0]] == ["lag", "corr_payroll", "corr_unrate"]
    body = [r for r in out[1:] if r and any(c.strip() for c in r)]
    assert len(body) == 13
    assert [int(float(r[0])) for r in body] == LAGS


def test_payroll_corr(out, expected):
    body = [r for r in out[1:] if r and any(c.strip() for c in r)]
    for r in body:
        k = int(float(r[0]))
        assert abs(float(r[1]) - expected[k][0]) < 2e-3, (k, r[1], expected[k][0])


def test_unrate_corr(out, expected):
    body = [r for r in out[1:] if r and any(c.strip() for c in r)]
    for r in body:
        k = int(float(r[0]))
        assert abs(float(r[2]) - expected[k][1]) < 2e-3, (k, r[2], expected[k][1])
