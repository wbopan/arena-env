#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_qubit_dynamics.py <<'PY'
import csv
import json
import numpy as np
from scipy.linalg import expm

data = json.load(open('qubit_runs.json'))
I = np.eye(2, dtype=complex)
Z = np.diag([1.,-1.])
X = np.array([[0.,1.],[1.,0.]])
Y = np.array([[0.,-1j],[1j,0.]])
s = np.array([[0.,1.],[0.,0.]])
A, B = np.kron(Z,I), np.kron(I,Z)
start = np.zeros(16, complex)
start[2+4*2] = 1
with open('qubit_dynamics.csv','w',newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['case_id','time','z1','z2','purity1'])
    for r in data['runs']:
        H = (r['omega1']*A+r['omega2']*B+r['exchange']*(np.kron(X,X)+np.kron(Y,Y)))/2
        c_ops = [np.sqrt(r['gamma1'])*np.kron(s,I), np.sqrt(r['gamma2'])*np.kron(I,s), np.sqrt(r['gamma_phi']/2)*A]
        L = -1j*(np.kron(np.eye(4),H)-np.kron(H.T,np.eye(4)))
        for c in c_ops:
            d = c.conj().T@c
            L += np.kron(c.conj(),c)-0.5*(np.kron(np.eye(4),d)+np.kron(d.T,np.eye(4)))
        for t in data['times']:
            rho = (expm(t*L)@start).reshape((4,4),order='F')
            rho1 = np.array([[rho[2*i,2*j]+rho[2*i+1,2*j+1] for j in range(2)] for i in range(2)])
            writer.writerow([r['case_id'],f'{t:.12f}',f'{np.trace(A@rho).real:.12f}',f'{np.trace(B@rho).real:.12f}',f'{np.trace(rho1@rho1).real:.12f}'])
PY
python /tmp/solve_qubit_dynamics.py
