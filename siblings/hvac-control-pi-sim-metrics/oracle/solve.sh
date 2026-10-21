#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_sim.py <<'EOF'
import json
import numpy as np

p = json.load(open('params.json'))
dt = p['dt']
N = int(round(p['duration'] / dt))
sp = p['setpoint']
T = np.zeros(N + 1)
T[0] = p['T0']
I = 0.0
u_hist = np.zeros(N)
cutoffs = 0
for k in range(N):
    e = sp - T[k]
    if T[k] >= p['T_max']:
        u = 0.0
        cutoffs += 1
    else:
        Ic = I + e * dt
        ur = p['Kp'] * e + p['Ki'] * Ic
        u = min(100.0, max(0.0, ur))
        if 0.0 <= ur <= 100.0:
            I = Ic
    u_hist[k] = u
    T[k + 1] = T[k] + dt / p['tau'] * (p['T_ambient'] + p['K'] * u - T[k])
t = np.arange(N + 1) * dt
T0 = p['T0']
idx = np.where(T >= T0 + 0.9 * (sp - T0))[0]
rise = float(t[idx[0]]) if len(idx) else None
out_idx = np.where(np.abs(T - sp) > p['settle_band'])[0]
if len(out_idx) == 0:
    settle = 0.0
elif out_idx[-1] == N:
    settle = None
else:
    settle = float(t[out_idx[-1] + 1])
mx = float(T.max())
m = max(1, int(np.floor(0.2 * (N + 1))))
res = {
    'rise_time': None if rise is None else round(rise, 3),
    'settling_time': None if settle is None else round(settle, 3),
    'overshoot_pct': round(max(0.0, (mx - sp) / (sp - T0)) * 100, 3),
    'max_temp': round(mx, 3),
    'steady_state_error': round(float(abs(T[-m:].mean() - sp)), 3),
    'mean_heater_power': round(float(u_hist.mean()), 3),
    'safety_cutoffs': int(cutoffs),
}
json.dump(res, open('metrics.json', 'w'), indent=2)
EOF
python3 /tmp/solve_sim.py
