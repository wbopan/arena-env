#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_advection.py <<'PY'
import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
from scipy.io import netcdf_file

config = Path('glm3.nml').read_text()
def paths(key):
    value = re.search(rf'(?im)^\s*{key}\s*=\s*([^\n]+)', config).group(1)
    return re.findall(r"'([^']+)'", value)
with open(paths('outflow_fl')[0]) as f:
    out = {row['date']: float(row['flow_m3_s']) for row in csv.DictReader(f)}
ins = {date: [] for date in out}
for path in paths('inflow_fl'):
    with open(path) as f:
        for row in csv.DictReader(f):
            ins[row['date']].append((float(row['flow_m3_s']), float(row['temp_C'])))
surface = {}
with netcdf_file('output/output.nc', 'r', mmap=False) as nc:
    hours = nc.variables['time'][:].copy()
    z = nc.variables['z'][:].copy()
    temp = nc.variables['temp'][:].copy()
for i, hour in enumerate(hours):
    date = (datetime(2009, 1, 1, 12) + timedelta(hours=float(hour))).date().isoformat()
    j = max(range(z.shape[1]), key=lambda j: z[i, j, 0, 0])
    surface[date] = float(temp[i, j, 0, 0])
with open('advective_budget.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['date', 'inflow_m3', 'outflow_m3', 'net_heat_MJ'])
    for date in sorted(out):
        vin = 86400 * sum(q for q, t in ins[date])
        vout = 86400 * out[date]
        heat = 4.186 * (86400 * sum(q*t for q, t in ins[date]) - vout * surface[date])
        writer.writerow([date, f'{vin:.3f}', f'{vout:.3f}', f'{heat:.3f}'])
PY
python /tmp/solve_advection.py
