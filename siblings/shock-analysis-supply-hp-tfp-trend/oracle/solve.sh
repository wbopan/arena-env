#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json
import numpy as np
import openpyxl
wb = openpyxl.load_workbook('macro_data.xlsx', data_only=True)
rows = sorted([r for r in wb['Macro'].iter_rows(min_row=2, values_only=True) if r[0] is not None], key=lambda r: int(r[0]))
prm = {str(r[0]).strip(): float(r[1]) for r in wb['Params'].iter_rows(min_row=2, values_only=True) if r[0] is not None}
a, lam = prm['alpha'], prm['hp_lambda']
yrs = [int(r[0]) for r in rows]
K = np.array([r[1] for r in rows], float)
Y = np.array([r[2] for r in rows], float)
C = np.array([r[3] for r in rows], float)
dep = float(np.mean((C / K)[-8:]))
z = np.log(Y) - a * np.log(K)
n = len(z)
D = np.diff(np.eye(n), 2, axis=0)
t = np.linalg.solve(np.eye(n) + lam * D.T @ D, z)
res = {'depreciation_rate': round(dep, 6), 'trend_growth_last': round(float(t[-1] - t[-2]), 6),
       'series': [{'year': y, 'lnZ': round(float(a1), 6), 'lnZ_trend': round(float(b1), 6)} for y, a1, b1 in zip(yrs, z, t)]}
json.dump(res, open('supply_trend.json', 'w'), indent=1)
EOF
python3 /tmp/solve.py
