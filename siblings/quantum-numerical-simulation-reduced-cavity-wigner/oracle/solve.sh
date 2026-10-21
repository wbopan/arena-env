#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import math
import numpy as np
from scipy.special import eval_genlaguerre

rho = np.loadtxt('rho_real.csv', delimiter=',') + 1j * np.loadtxt('rho_imag.csv', delimiter=',')
nc = rho.shape[0] // 2
rc = np.zeros((nc, nc), dtype=complex)
for s in range(2):
    rc += rho[s::2, s::2]
xs = np.linspace(-3, 3, 31)
rows = []
for x in xs:
    for p in xs:
        b = math.sqrt(2) * (x + 1j * p)
        r = abs(b) ** 2
        tot = 0j
        for m in range(nc):
            for n in range(nc):
                k = abs(n - m)
                lo = min(m, n)
                pref = math.sqrt(math.factorial(lo) / math.factorial(lo + k)) * math.exp(-r / 2) * eval_genlaguerre(lo, k, r)
                ph = b ** k if n >= m else (-np.conj(b)) ** k
                tot += rc[m, n] * (-1) ** m * pref * ph
        rows.append((x, p, tot.real / math.pi))
with open('wigner.csv', 'w') as f:
    f.write('x,p,W\n')
    for x, p, w in rows:
        f.write(f'{x:.10f},{p:.10f},{w:.12e}\n')
EOF
python3 /tmp/solve.py
