import csv
import math
from pathlib import Path
import numpy as np
from scipy.special import eval_genlaguerre

ROOT = Path('/root/work')
OUT = ROOT / 'wigner_samples.csv'
FIELDS = ['case_id', 'point_id', 'x', 'p', 'wigner']

def inputs():
    with (ROOT / 'cavity_cases.csv').open() as f:
        cases = list(csv.DictReader(f))
    with (ROOT / 'phase_points.csv').open() as f:
        points = list(csv.DictReader(f))
    return cases, points

def answer():
    cases, points = inputs()
    a = np.zeros((5, 5), complex)
    for n in range(1, 5):
        a[n-1, n] = np.sqrt(n)
    ad = a.conj().T
    ident = np.eye(5)
    number = ad @ a
    result = []
    for case in cases:
        h = float(case['detuning']) * number + float(case['drive']) * (a + ad)
        loss = np.sqrt(float(case['kappa']) * (1 + float(case['n_thermal']))) * a
        gain = np.sqrt(float(case['kappa']) * float(case['n_thermal'])) * ad
        # Column-major vectorization: vec(A rho B)=(B^T tensor A)vec(rho).
        li = -1j * (np.kron(ident, h) - np.kron(h.T, ident))
        for c in (loss, gain):
            d = c.conj().T @ c
            li += np.kron(c.conj(), c) - 0.5 * (np.kron(ident, d) + np.kron(d.T, ident))
        rhs = np.zeros(25, complex)
        li[0, :] = np.eye(5).reshape(-1, order='F')
        rhs[0] = 1
        rho = np.linalg.solve(li, rhs).reshape((5, 5), order='F')
        for point in points:
            x, p = float(point['x']), float(point['p'])
            r2 = x*x + p*p
            z = np.sqrt(2) * (x + 1j*p)
            value = 0j
            for m in range(5):
                for n in range(5):
                    if m >= n:
                        kernel = (-1)**n * np.sqrt(math.factorial(n)/math.factorial(m)) * z**(m-n) * eval_genlaguerre(n, m-n, 2*r2)
                    else:
                        kernel = (-1)**m * np.sqrt(math.factorial(m)/math.factorial(n)) * z.conjugate()**(n-m) * eval_genlaguerre(m, n-m, 2*r2)
                    value += rho[m, n] * kernel
            result.append((case['case_id'], point['point_id'], x, p, float((np.exp(-r2)*value/np.pi).real)))
    return result

def rows():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        data = list(reader)
    return fields, data

def test_file_exists():
    assert OUT.is_file()

def test_schema_and_count():
    fields, data = rows()
    cases, points = inputs()
    assert fields == FIELDS
    assert len(data) == len(cases)*len(points)

def test_order_and_coordinates():
    _, data = rows()
    for actual, expected in zip(data, answer(), strict=True):
        assert (actual['case_id'], actual['point_id']) == expected[:2]
        assert abs(float(actual['x'])-expected[2]) < 1e-9
        assert abs(float(actual['p'])-expected[3]) < 1e-9

def test_wigner_values():
    _, data = rows()
    for row, expected in zip(data, answer(), strict=True):
        value = float(row['wigner'])
        assert np.isfinite(value)
        assert abs(value-expected[4]) <= 2e-8
