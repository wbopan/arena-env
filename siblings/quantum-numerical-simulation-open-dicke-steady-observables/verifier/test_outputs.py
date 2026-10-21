from pathlib import Path

import numpy as np
import pandas as pd
import pytest

WORK = Path('/root/work')
OUT = WORK / 'results.csv'
NMAX = 10
TOL = 2e-5


def steady(row):
    a = np.diag(np.sqrt(np.arange(1, NMAX)), 1).astype(complex)
    sm = np.array([[0, 1], [0, 0]], dtype=complex)
    sz = np.diag([-1.0, 1.0]).astype(complex)
    I2 = np.eye(2)
    Ic = np.eye(NMAX)
    A = np.kron(a, np.eye(4))
    s1 = np.kron(Ic, np.kron(sm, I2))
    s2 = np.kron(Ic, np.kron(I2, sm))
    z1 = np.kron(Ic, np.kron(sz, I2))
    z2 = np.kron(Ic, np.kron(I2, sz))
    Jm = s1 + s2
    Jp = Jm.conj().T
    Jz = 0.5 * (z1 + z2)
    Ad = A.conj().T
    H = row.omega0 * Jz + row.omegac * Ad @ A + row.g * (A + Ad) @ (Jp + Jm)
    cops = [np.sqrt(row.kappa) * A, np.sqrt(row.gamma_down) * s1, np.sqrt(row.gamma_down) * s2,
            np.sqrt(row.gamma_phi) * z1, np.sqrt(row.gamma_phi) * z2]
    if row.gamma_cpump > 0:
        cops.append(np.sqrt(row.gamma_cpump) * Jp)
    d = H.shape[0]
    I = np.eye(d)
    L = -1j * (np.kron(I, H) - np.kron(H.T, I))
    for C in cops:
        CdC = C.conj().T @ C
        L += np.kron(C.conj(), C) - 0.5 * np.kron(I, CdC) - 0.5 * np.kron(CdC.T, I)
    M = L.copy()
    M[0, :] = 0
    M[0, np.arange(d) * (d + 1)] = 1
    b = np.zeros(d * d, dtype=complex)
    b[0] = 1
    v = np.linalg.solve(M, b)
    rho = v.reshape(d, d, order='F')
    rho = 0.5 * (rho + rho.conj().T)
    n = np.trace(rho @ Ad @ A).real
    jz = np.trace(rho @ Jz).real
    rc = np.einsum('iaja->ij', rho.reshape(NMAX, 4, NMAX, 4))
    pur = np.trace(rc @ rc).real
    return n, jz, pur


@pytest.fixture(scope='module')
def ref():
    cases = pd.read_csv(WORK / 'cases.csv')
    out = []
    for row in cases.itertuples():
        out.append((int(row.case_id),) + steady(row))
    return pd.DataFrame(out, columns=['case_id', 'n_photon', 'jz', 'cavity_purity'])


@pytest.fixture(scope='module')
def df():
    assert OUT.exists(), 'results.csv missing'
    return pd.read_csv(OUT)


def test_exists():
    assert OUT.exists()


def test_schema(df, ref):
    assert list(df.columns) == ['case_id', 'n_photon', 'jz', 'cavity_purity']
    assert df['case_id'].astype(int).tolist() == ref['case_id'].tolist()


def test_n_photon(df, ref):
    assert np.max(np.abs(df['n_photon'].to_numpy(float) - ref['n_photon'].to_numpy())) < TOL


def test_jz(df, ref):
    assert np.max(np.abs(df['jz'].to_numpy(float) - ref['jz'].to_numpy())) < TOL


def test_purity(df, ref):
    assert np.max(np.abs(df['cavity_purity'].to_numpy(float) - ref['cavity_purity'].to_numpy())) < TOL
