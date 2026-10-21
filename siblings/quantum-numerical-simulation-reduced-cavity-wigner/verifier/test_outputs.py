import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.special import eval_genlaguerre

WORK = Path('/root/work')
OUT = WORK / 'wigner.csv'
TOL = 1e-6


def reference():
    rho = np.loadtxt(WORK / 'rho_real.csv', delimiter=',') + 1j * np.loadtxt(WORK / 'rho_imag.csv', delimiter=',')
    nc = rho.shape[0] // 2
    rc = np.einsum('iaja->ij', rho.reshape(nc, 2, nc, 2))
    xs = np.linspace(-3, 3, 31)
    X, P = np.meshgrid(xs, xs, indexing='ij')
    beta = 2 * (X + 1j * P) / np.sqrt(2)
    b2 = np.abs(beta) ** 2
    W = np.zeros(X.shape, dtype=complex)
    for m in range(nc):
        for n in range(nc):
            if n >= m:
                el = math.sqrt(math.factorial(m) / math.factorial(n)) * beta ** (n - m) * np.exp(-b2 / 2) * eval_genlaguerre(m, n - m, b2)
            else:
                el = math.sqrt(math.factorial(n) / math.factorial(m)) * (-np.conj(beta)) ** (m - n) * np.exp(-b2 / 2) * eval_genlaguerre(n, m - n, b2)
            W += rc[m, n] * (-1) ** m * el
    return X.ravel(), P.ravel(), (W.real / np.pi).ravel()


@pytest.fixture(scope='module')
def df():
    assert OUT.exists(), 'wigner.csv missing'
    return pd.read_csv(OUT)


def test_file_exists():
    assert OUT.exists()


def test_columns(df):
    assert list(df.columns) == ['x', 'p', 'W']


def test_grid(df):
    X, P, _ = reference()
    assert len(df) == 961
    assert np.allclose(df['x'].to_numpy(float), X, atol=1e-9)
    assert np.allclose(df['p'].to_numpy(float), P, atol=1e-9)


def test_finite(df):
    assert np.all(np.isfinite(df['W'].to_numpy(float)))


def test_values(df):
    _, _, W = reference()
    got = df['W'].to_numpy(float)
    assert np.max(np.abs(got - W)) < TOL
