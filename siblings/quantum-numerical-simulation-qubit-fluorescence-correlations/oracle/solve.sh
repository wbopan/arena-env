#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_fluorescence.py <<'PY'
import csv
import json
import numpy as np
from scipy.linalg import expm

source = json.load(open('fluorescence_cases.json'))
I = np.eye(2)
Z = np.diag([1.,-1.])
X = np.array([[0.,1.],[1.,0.]])
minus = np.array([[0.,1.],[0.,0.]])
plus = minus.T
with open('fluorescence.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['case_id','delay','population','c_real','c_imag'])
    for r in source['cases']:
        H = (r['detuning']*Z+r['rabi']*X)/2
        L = -1j*(np.kron(I,H)-np.kron(H.T,I))
        for c in (np.sqrt(r['gamma_down'])*minus,np.sqrt(r['gamma_phi']/2)*Z):
            d = c.T.conj()@c
            L += np.kron(c.conj(),c)-0.5*(np.kron(I,d)+np.kron(d.T,I))
        system = L.copy()
        system[0,:] = [1,0,0,1]
        rhs = np.array([1,0,0,0],complex)
        rho = np.linalg.solve(system,rhs).reshape((2,2),order='F')
        population = np.trace(plus@minus@rho).real
        initial = (minus@rho).reshape(4,order='F')
        for delay in source['delays']:
            propagated = (expm(delay*L)@initial).reshape((2,2),order='F')
            C = np.trace(plus@propagated)
            w.writerow([r['case_id'],f'{delay:.12f}',f'{population:.12f}',f'{C.real:.12f}',f'{C.imag:.12f}'])
PY
python /tmp/solve_fluorescence.py
