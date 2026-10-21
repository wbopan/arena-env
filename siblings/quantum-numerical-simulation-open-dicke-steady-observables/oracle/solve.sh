#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv
import numpy as np
from scipy.linalg import svd

NM = 10
sm = np.array([[0, 1], [0, 0]], dtype=complex)
sz = np.diag([-1.0, 1.0]).astype(complex)
a = np.diag(np.sqrt(np.arange(1, NM)), 1).astype(complex)
def emb(c, q1, q2):
    return np.kron(c, np.kron(q1, q2))
Ic = np.eye(NM); I2 = np.eye(2)
A = emb(a, I2, I2)
s1 = emb(Ic, sm, I2); s2 = emb(Ic, I2, sm)
z1 = emb(Ic, sz, I2); z2 = emb(Ic, I2, sz)
Jm = s1 + s2; Jp = Jm.conj().T; Jz = 0.5 * (z1 + z2)
Num = A.conj().T @ A
d = A.shape[0]
I = np.eye(d)
rows = []
with open('cases.csv') as f:
    for r in csv.DictReader(f):
        v = {k: float(x) for k, x in r.items()}
        H = v['omega0'] * Jz + v['omegac'] * Num + v['g'] * (A + A.conj().T) @ (Jp + Jm)
        cops = [np.sqrt(v['kappa']) * A, np.sqrt(v['gamma_down']) * s1, np.sqrt(v['gamma_down']) * s2,
                np.sqrt(v['gamma_phi']) * z1, np.sqrt(v['gamma_phi']) * z2]
        if v['gamma_cpump'] > 0:
            cops.append(np.sqrt(v['gamma_cpump']) * Jp)
        L = -1j * (np.kron(H, I) - np.kron(I, H.T))
        for C in cops:
            CdC = C.conj().T @ C
            L += np.kron(C, C.conj()) - 0.5 * np.kron(CdC, I) - 0.5 * np.kron(I, CdC.T)
        _, _, Vh = svd(L)
        rho = Vh[-1].conj().reshape(d, d)
        rho = rho / np.trace(rho)
        rho = 0.5 * (rho + rho.conj().T)
        n = np.trace(rho @ Num).real
        jz = np.trace(rho @ Jz).real
        rc = rho.reshape(NM, 4, NM, 4).trace(axis1=1, axis2=3)
        pur = np.trace(rc @ rc).real
        rows.append((int(v['case_id']), n, jz, pur))
with open('results.csv', 'w') as f:
    f.write('case_id,n_photon,jz,cavity_purity\n')
    for c, n, jz, p in rows:
        f.write(f'{c},{n:.6f},{jz:.6f},{p:.6f}\n')
EOF
python3 /tmp/solve.py
