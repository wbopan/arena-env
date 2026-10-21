#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
VP = 6.0
VS = VP / 1.75
DEPTH = 10.0
sta = pd.read_csv('stations.csv').drop_duplicates(['network', 'station']).copy()
lat0 = sta['latitude'].mean()
lon0 = sta['longitude'].mean()
sta['x'] = (sta['longitude'] - lon0) * 111.19 * np.cos(np.radians(lat0))
sta['y'] = (sta['latitude'] - lat0) * 111.19
sta['dz'] = DEPTH + sta['elevation_m'] / 1000.0
sta.index = sta['network'] + '.' + sta['station']
pk = pd.read_csv('picks.csv')
pk['sid'] = pk['network'] + '.' + pk['station']
ref = pd.Timestamp('2000-01-01')
pk['t'] = (pd.to_datetime(pk['timestamp']) - ref).dt.total_seconds()
rows = []
for eid, g in pk.groupby('event_id'):
    sx = sta.loc[g['sid'], 'x'].to_numpy()
    sy = sta.loc[g['sid'], 'y'].to_numpy()
    dz = sta.loc[g['sid'], 'dz'].to_numpy()
    v = np.where(g['phase'].str.upper() == 'P', VP, VS)
    t = g['t'].to_numpy()
    tref = t.min()
    tr = t - tref
    def f(p):
        return p[2] + np.sqrt((p[0] - sx) ** 2 + (p[1] - sy) ** 2 + dz ** 2) / v - tr
    k = int(np.argmin(tr))
    sol = least_squares(f, [sx[k], sy[k], -2.0], xtol=1e-12, ftol=1e-12, gtol=1e-12)
    x, y, t0 = sol.x
    rms = float(np.sqrt(np.mean(f(sol.x) ** 2)))
    otime = ref + pd.Timedelta(seconds=float(tref + t0))
    rows.append({'event_id': int(eid), 'time': otime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
                 'x_km': round(float(x), 3), 'y_km': round(float(y), 3), 'rms_s': round(rms, 4)})
pd.DataFrame(rows).to_csv('locations.csv', index=False)
EOF
python3 /tmp/solve.py
