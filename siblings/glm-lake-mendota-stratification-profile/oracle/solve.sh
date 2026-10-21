#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_strat.py <<'EOF'
import re, csv
import numpy as np
import pandas as pd
from scipy.io import netcdf_file

txt = open('glm3.nml').read()
sec = re.search(r'&init_profiles(.*?)\n/', txt, re.S).group(1)
ld = float(re.search(r'lake_depth\s*=\s*([-+\d.eE]+)', sec).group(1))
tsec = re.search(r'&time(.*?)\n/', txt, re.S).group(1)
start = pd.Timestamp(re.search(r"start\s*=\s*'([^']+)'", tsec).group(1))

def rho(T):
    return 1000.0 * (1.0 - (T + 288.9414) / (508929.2 * (T + 68.12963)) * (T - 3.9863) ** 2)

f = netcdf_file('output/output.nc', 'r', mmap=False)
time = np.array(f.variables['time'][:], dtype=float)
ns = np.array(f.variables['NS'][:]).astype(int)
z = np.array(f.variables['z'][:], dtype=float)
tp = np.array(f.variables['temp'][:], dtype=float)
f.close()
with open('stratification.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['datetime', 'surface_temp', 'bottom_temp', 'density_diff', 'stratified', 'thermocline_depth'])
    for i in range(len(time)):
        n = ns[i]
        d = ld - z[i, :n, 0, 0]
        T = tp[i, :n, 0, 0]
        o = np.argsort(d)
        d, T = d[o], T[o]
        dr = rho(T[-1]) - rho(T[0])
        st = int(dr > 0.1)
        th = ''
        if st:
            g = np.abs(np.diff(T)) / np.diff(d)
            k = int(np.argmax(g))
            th = f'{0.5 * (d[k] + d[k + 1]):.2f}'
        dt = (start + pd.Timedelta(hours=float(time[i]))).strftime('%Y-%m-%d %H:%M')
        w.writerow([dt, f'{T[0]:.3f}', f'{T[-1]:.3f}', f'{dr:.4f}', st, th])
EOF
python3 /tmp/solve_strat.py
