#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_rmse.py <<'EOF'
import re, json
import numpy as np
import pandas as pd
from scipy.io import netcdf_file

txt = open('glm3.nml').read()
sec = re.search(r'&init_profiles(.*?)\n/', txt, re.S).group(1)
ld = float(re.search(r'lake_depth\s*=\s*([-+\d.eE]+)', sec).group(1))
f = netcdf_file('output/output.nc', 'r', mmap=False)
time = np.array(f.variables['time'][:], dtype=float)
z = np.array(f.variables['z'][:], dtype=float)
tp = np.array(f.variables['temp'][:], dtype=float)
f.close()
start = pd.Timestamp('2009-01-01 12:00:00')
rec = []
for i, h in enumerate(time):
    dt = start + pd.Timedelta(hours=float(h))
    for j in range(z.shape[1]):
        zz = z[i, j, 0, 0]; tt = tp[i, j, 0, 0]
        if abs(zz) > 1e30 or abs(tt) > 1e30:
            continue
        d = ld - zz
        if 0 <= d <= ld:
            rec.append((dt, int(round(d)), tt))
sim = pd.DataFrame(rec, columns=['datetime', 'depth', 'temp_sim']).groupby(['datetime', 'depth'], as_index=False)['temp_sim'].mean()
obs = pd.read_csv('field_temp_oxy.csv')
obs['datetime'] = pd.to_datetime(obs['datetime'])
obs['depth'] = obs['depth'].round().astype(int)
m = obs.merge(sim, on=['datetime', 'depth'], how='inner')
diff = m['temp_sim'] - m['temp']
res = {'rmse': round(float(np.sqrt(np.mean(diff ** 2))), 4), 'bias': round(float(diff.mean()), 4), 'n_matched': int(len(m))}
json.dump(res, open('rmse.json', 'w'))
print(res)
EOF
python3 /tmp/solve_rmse.py
