#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_cavity_wigner.py <<'PY'
import csv
from math import factorial, pi
import numpy as np
from scipy.special import eval_genlaguerre

with open('cavity_cases.csv') as f:
    cases = list(csv.DictReader(f))
with open('phase_points.csv') as f:
    points = list(csv.DictReader(f))
a = np.diag(np.sqrt(np.arange(1, 5)), 1).astype(complex)
ad = a.T.conj()
I = np.eye(5)
nop = ad @ a
with open('wigner_samples.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['case_id', 'point_id', 'x', 'p', 'wigner'])
    for c in cases:
        delta, drive, kappa, nt = (float(c[k]) for k in ('detuning', 'drive', 'kappa', 'n_thermal'))
        H = delta*nop + drive*(a+ad)
        L = -1j*(np.kron(I, H)-np.kron(H.T, I))
        for op in (np.sqrt(kappa*(nt+1))*a, np.sqrt(kappa*nt)*ad):
            q = op.conj().T @ op
            L += np.kron(op.conj(), op)-0.5*np.kron(I,q)-0.5*np.kron(q.T,I)
        b = np.zeros(25, complex)
        b[0] = 1
        L[0, :] = I.reshape(-1, order='F')
        rho = np.linalg.solve(L,b).reshape((5,5),order='F')
        for point in points:
            x, p = float(point['x']), float(point['p'])
            r = x*x+p*p
            z = np.sqrt(2)*(x+1j*p)
            v = 0j
            for m in range(5):
                for n in range(5):
                    low, high = min(m,n), max(m,n)
                    term = z**(high-low) if m >= n else z.conjugate()**(high-low)
                    v += rho[m,n]*(-1)**low*np.sqrt(factorial(low)/factorial(high))*term*eval_genlaguerre(low,high-low,2*r)
            w.writerow([c['case_id'], point['point_id'], point['x'], point['p'], f'{(np.exp(-r)*v/pi).real:.12f}'])
PY
python /tmp/solve_cavity_wigner.py
