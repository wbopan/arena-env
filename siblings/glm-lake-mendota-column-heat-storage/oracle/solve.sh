#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_storage.py <<'PY'
import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

config = Path('glm3.nml').read_text()
depth = float(re.search(r'(?im)^\s*lake_depth\s*=\s*([\d.]+)', config).group(1))
with open('bcs/hypsography.csv') as f:
    pairs = sorted((float(r['height_m']), float(r['area_m2'])) for r in csv.DictReader(f))
heights, areas = zip(*pairs)
with netcdf_file('output/output.nc', 'r', mmap=False) as nc:
    times = nc.variables['time'][:].copy()
    z = nc.variables['z'][:].copy()
    temps = nc.variables['temp'][:].copy()
rows = []
previous = None
for i, hour in enumerate(times):
    layers = sorted((float(z[i, j, 0, 0]), float(temps[i, j, 0, 0])) for j in range(z.shape[1]))
    edges = [0.] + [(layers[j][0] + layers[j+1][0])/2 for j in range(len(layers)-1)] + [depth]
    edge_areas = np.interp(edges, heights, areas)
    heat = sum((edges[j+1]-edges[j]) * (edge_areas[j]+edge_areas[j+1])/2 * layers[j][1] for j in range(len(layers))) * 4.186/1000
    stamp = (datetime(2009, 1, 1, 12) + timedelta(hours=float(hour))).isoformat()
    rows.append({'datetime': stamp, 'heat_GJ': round(heat, 3), 'delta_GJ': round(0. if previous is None else heat-previous, 3)})
    previous = heat
Path('heat_storage.json').write_text(json.dumps(rows, indent=2) + '\n')
PY
python /tmp/solve_storage.py
