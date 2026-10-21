#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, json, re
import numpy as np
import openpyxl
YEARS = list(range(1980, 2025))

def load(p):
    ws = openpyxl.load_workbook(p, data_only=True)['Table']
    ann, qs = {}, {}
    for row in ws.iter_rows(min_row=4, values_only=True):
        k, v = row[0], row[1] if len(row) > 1 else None
        if v is None or not isinstance(v, (int, float)):
            continue
        if isinstance(k, (int, float)):
            ann[int(k)] = float(v)
        elif isinstance(k, str):
            m = re.match(r'^(\d{4}):\s*(I|II|III|IV)$', k.strip())
            if m:
                qs.setdefault(int(m.group(1)), []).append(float(v))
    return np.array([ann.get(y, np.mean(qs.get(y, [np.nan]))) for y in YEARS])

def hp(y, lam):
    T = len(y)
    D = np.diff(np.eye(T), 2, axis=0)
    return y - np.linalg.solve(np.eye(T) + lam * D.T @ D, y)

cp = {}
for r in csv.DictReader(open('cpi_monthly.csv')):
    cp.setdefault(int(r['observation_date'][:4]), []).append(float(r['CPIAUCSL']))
cpi = np.array([np.mean(cp[y]) for y in YEARS])
cc = hp(np.log(load('pce_nominal.xlsx') / cpi * 100), 100)
ci = hp(np.log(load('pfi_nominal.xlsx') / cpi * 100), 100)
sc = np.std(cc, ddof=1) * 100
si = np.std(ci, ddof=1) * 100
res = {'n_years': len(YEARS), 'std_pce_pct': round(float(sc), 4), 'std_pfi_pct': round(float(si), 4),
       'relative_volatility': round(float(si / sc), 4), 'corr': round(float(np.corrcoef(cc, ci)[0, 1]), 4)}
json.dump(res, open('cycle_stats.json', 'w'), indent=2)
print(res)
EOF
python3 /tmp/solve.py
