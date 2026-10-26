import csv
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm

ROOT = Path('/root/work')
OUT = ROOT / 'fluorescence.csv'
FIELDS = ['case_id','delay','population','c_real','c_imag']

def expected():
    data = json.loads((ROOT/'fluorescence_cases.json').read_text())
    eye = np.eye(2)
    z = np.diag([1.,-1.])
    x = np.array([[0.,1.],[1.,0.]])
    sm = np.array([[0.,1.],[0.,0.]])
    sp = sm.T
    result = []
    for case in data['cases']:
        H = (case['detuning']*z+case['rabi']*x)/2
        L = -1j*(np.kron(eye,H)-np.kron(H.T,eye))
        for c in (np.sqrt(case['gamma_down'])*sm, np.sqrt(case['gamma_phi']/2)*z):
            d = c.conj().T@c
            L += np.kron(c.conj(),c)-0.5*np.kron(eye,d)-0.5*np.kron(d.T,eye)
        A = L.copy()
        A[0,:] = np.array([1,0,0,1])
        b = np.array([1,0,0,0],complex)
        steady = np.linalg.solve(A,b).reshape((2,2),order='F')
        pop = float(np.trace(sp@sm@steady).real)
        seed = (sm@steady).reshape(4,order='F')
        for delay in data['delays']:
            evolved = (expm(delay*L)@seed).reshape((2,2),order='F')
            corr = np.trace(sp@evolved)
            result.append((case['case_id'],delay,pop,corr.real,corr.imag))
    return result

def output():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames,list(reader)

def test_file_exists():
    assert OUT.is_file()

def test_schema_and_count():
    fields,rows = output()
    assert fields == FIELDS
    assert len(rows) == len(expected())

def test_case_delay_order():
    _,rows = output()
    for row,ref in zip(rows,expected(),strict=True):
        assert row['case_id'] == ref[0]
        assert abs(float(row['delay'])-ref[1]) < 1e-9

def test_populations():
    _,rows = output()
    for row,ref in zip(rows,expected(),strict=True):
        value = float(row['population'])
        assert 0 <= value <= 1
        assert abs(value-ref[2]) < 2e-8

def test_complex_correlations():
    _,rows = output()
    for row,ref in zip(rows,expected(),strict=True):
        for key,value in zip(('c_real','c_imag'),ref[3:]):
            got = float(row[key])
            assert np.isfinite(got)
            assert abs(got-value) < 2e-8
