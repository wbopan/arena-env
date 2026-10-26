#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_light.py <<'PY'
import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
from scipy.io import netcdf_file

text = Path('glm3.nml').read_text()
kw = float(re.search(r'(?im)^\s*Kw\s*=\s*([\d.eE+-]+)', text).group(1))
lake_depth = float(re.search(r'(?im)^\s*lake_depth\s*=\s*([\d.eE+-]+)', text).group(1))
with open('bcs/meteo.csv') as f:
    solar = {r['datetime']: float(r['shortwave_W_m2']) for r in csv.DictReader(f)}
sim = {}
with netcdf_file('output/output.nc', 'r', mmap=False) as nc:
    times = nc.variables['time'][:].copy()
    z = nc.variables['z'][:].copy()
    temp = nc.variables['temp'][:].copy()
for i, hour in enumerate(times):
    date = (datetime(2009, 1, 1, 12) + timedelta(hours=float(hour))).isoformat()
    for j in range(z.shape[1]):
        sim[date, round(lake_depth - float(z[i, j, 0, 0]), 6)] = float(temp[i, j, 0, 0])
xy = xx = 0.
with open('field_temp_oxy.csv') as f:
    for r in csv.DictReader(f):
        date, depth = r['datetime'], float(r['depth_m'])
        key = (date, round(depth, 6))
        if key not in sim or date not in solar:
            continue
        x = (depth - 10) * solar[date] / 200
        xy += x * (float(r['temp_C']) - sim[key])
        xx += x*x
new_kw = kw + xy / xx
text = re.sub(r'(?im)^(\s*Kw\s*=\s*)([\d.eE+-]+)', lambda m: m.group(1) + f'{new_kw:.4f}', text)
Path('calibrated_glm3.nml').write_text(text)
PY
python /tmp/solve_light.py
