#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv
import numpy as np

rows = sorted(csv.DictReader(open('indicators.csv')), key=lambda r: r['month'])

def hp(y, lam):
    y = np.asarray(y, float)
    T = len(y)
    D = np.diff(np.eye(T), 2, axis=0)
    return y - np.linalg.solve(np.eye(T) + lam * D.T @ D, y)

ip = hp(np.log([float(r['ip_index']) for r in rows]), 14400)
pay = hp(np.log([float(r['payroll_thousands']) for r in rows]), 14400)
ur = hp([float(r['unemployment_rate']) for r in rows], 14400)
T = len(ip)

def lc(a, b, k):
    if k >= 0:
        return np.corrcoef(a[:T - k], b[k:])[0, 1]
    return np.corrcoef(a[-k:], b[:T + k])[0, 1]

with open('lead_lag.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['lag', 'corr_payroll', 'corr_unrate'])
    for k in range(-6, 7):
        w.writerow([k, f'{lc(ip, pay, k):.4f}', f'{lc(ip, ur, k):.4f}'])
print(open('lead_lag.csv').read())
EOF
python3 /tmp/solve.py
