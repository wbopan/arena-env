import csv
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm

ROOT = Path('/root/work')
OUT = ROOT / 'qubit_dynamics.csv'
FIELDS = ['case_id', 'time', 'z1', 'z2', 'purity1']

def expected():
    data = json.loads((ROOT / 'qubit_runs.json').read_text())
    eye = np.eye(2, dtype=complex)
    z = np.diag([1, -1]).astype(complex)
    x = np.array([[0, 1], [1, 0]], complex)
    y = np.array([[0, -1j], [1j, 0]], complex)
    lower = np.array([[0, 1], [0, 0]], complex)
    z1, z2 = np.kron(z, eye), np.kron(eye, z)
    initial = np.zeros((4,4), complex)
    initial[2,2] = 1
    results = []
    for run in data['runs']:
        H = run['omega1']*z1/2 + run['omega2']*z2/2 + run['exchange']*(np.kron(x,x)+np.kron(y,y))/2
        ops = [np.sqrt(run['gamma1'])*np.kron(lower,eye), np.sqrt(run['gamma2'])*np.kron(eye,lower), np.sqrt(run['gamma_phi']/2)*z1]
        ident = np.eye(4)
        L = -1j*(np.kron(ident,H)-np.kron(H.T,ident))
        for c in ops:
            d = c.conj().T @ c
            L += np.kron(c.conj(),c)-0.5*np.kron(ident,d)-0.5*np.kron(d.T,ident)
        for t in data['times']:
            rho = (expm(t*L) @ initial.reshape(16,order='F')).reshape((4,4),order='F')
            reduced = np.einsum('abcb->ac', rho.reshape(2,2,2,2))
            results.append((run['case_id'], t, (np.trace(z1@rho)).real, (np.trace(z2@rho)).real, (np.trace(reduced@reduced)).real))
    return results

def output():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def test_exists():
    assert OUT.is_file()

def test_columns_and_row_count():
    fields, rows = output()
    assert fields == FIELDS
    assert len(rows) == len(expected())

def test_run_and_time_order():
    _, rows = output()
    for row, ref in zip(rows, expected(), strict=True):
        assert row['case_id'] == ref[0]
        assert abs(float(row['time']) - ref[1]) < 1e-9

def test_expectations():
    _, rows = output()
    for row, ref in zip(rows, expected(), strict=True):
        for key, val in zip(('z1','z2'), ref[2:4]):
            assert np.isfinite(float(row[key]))
            assert abs(float(row[key])-val) < 2e-8

def test_reduced_purity():
    _, rows = output()
    for row, ref in zip(rows, expected(), strict=True):
        p = float(row['purity1'])
        assert 0.5-2e-8 <= p <= 1+2e-8
        assert abs(p-ref[4]) < 2e-8
