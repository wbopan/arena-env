#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_step.py <<'EOF'
import json
import numpy as np
import pandas as pd

df = pd.read_csv('/root/work/flights.csv')
with open('/root/work/targets.json') as f:
    targets = json.load(f)
out = {}
for fid, tgt in targets.items():
    g = df[df['flight_id'] == int(fid)].sort_values('t')
    t = g['t'].to_numpy(dtype=float)
    p = g[['x', 'y', 'z']].to_numpy(dtype=float)
    d = np.linalg.norm(p - np.array(tgt, dtype=float), axis=1)
    d0 = d[0]
    if d0 < 1e-6:
        out[fid] = {'RiseTime': 0.0, 'SettlingTime': 0.0, 'Overshoot_pct': 0.0, 'SteadyStateError': 0.0}
        continue
    band = 0.02 * d0
    rise = None
    for k in range(len(d)):
        if d[k] <= 0.1 * d0:
            rise = round(float(t[k]), 4)
            break
    settle = 0.0
    for k in range(len(d) - 1, -1, -1):
        if d[k] > band:
            settle = float(t[k])
            break
    ov = 0.0
    for k in range(len(d)):
        if d[k] <= band:
            ov = float(d[k:].max() / d0 * 100.0)
            break
    out[fid] = {'RiseTime': rise, 'SettlingTime': round(settle, 4),
                'Overshoot_pct': round(ov, 4), 'SteadyStateError': round(float(d[-1]), 4)}
with open('/root/work/step_metrics.json', 'w') as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve_step.py
