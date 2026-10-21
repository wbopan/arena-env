#!/bin/bash
set -e
cat > /tmp/aic.py <<'EOF'
import glob, os, json
import numpy as np
os.chdir('/root/work')

def aic(y):
    y = np.asarray(y, float)
    y = y - y.mean()
    M = len(y)
    best = None
    bk = None
    for k in range(10, M - 10):
        v = k * np.log(np.var(y[:k])) + (M - k - 1) * np.log(np.var(y[k:]))
        if best is None or v < best:
            best = v
            bk = k
    return bk

out = {}
for f in sorted(glob.glob('sta_*.npz')):
    d = np.load(f)
    dt = float(d['dt'])
    code = str(d['station'])
    names = [c.strip() for c in str(d['channels']).split(',')]
    z = [k for k, c in enumerate(names) if c.endswith('Z')][0]
    n = [k for k, c in enumerate(names) if c.endswith('N')][0]
    data = d['data'].astype(float)
    p = aic(data[:, z])
    w = p + int(round(0.2 / dt))
    s = w + aic(data[w:, n])
    sp = (s - p) * dt
    out[code] = {'p_idx': int(p), 's_idx': int(s), 'sp_time_s': round(sp, 3),
                 'distance_km': round(sp * 6.0 * 3.5 / 2.5, 2)}
nearest = min(out, key=lambda c: out[c]['distance_km'])
with open('picks.json', 'w') as fh:
    json.dump({'stations': out, 'nearest_station': nearest}, fh, indent=2)
EOF
python3 /tmp/aic.py
