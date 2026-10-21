#!/bin/bash
set -e
mkdir -p /root/work/output
cat > /tmp/solve_ramp.py <<'EOF'
import json
import pandas as pd

W = '/root/work'
# values read from handbook.md (rev D, current)
TMIN, TMAX, LIMIT = 100.0, 150.0, 2.0
OVEN = {'OV-A': 360.0, 'OV-B': 420.0, 'OV-C': 300.0}
MIN_DWELL = {'THIN': 150.0, 'STD': 180.0, 'THICK': 220.0}
MAX_DWELL = 330.0

mes = pd.read_csv(f'{W}/mes_log.csv', dtype={'run_id': str}).sort_values('run_id')
tc = pd.read_csv(f'{W}/thermocouples.csv', dtype={'run_id': str, 'tc_id': str})
runs = []
for _, r in mes.iterrows():
    g = tc[tc.run_id == r.run_id]
    best = None
    for tcid in sorted(g.tc_id.unique()):
        h = g[g.tc_id == tcid].sort_values('time_s', kind='mergesort')
        t = h.time_s.to_numpy(float)
        y = h.temp_c.to_numpy(float)
        m = None
        for i in range(1, len(t)):
            dt = t[i] - t[i-1]
            if dt > 0 and TMIN <= y[i-1] <= TMAX and TMIN <= y[i] <= TMAX:
                s = (y[i] - y[i-1]) / dt
                m = s if m is None else max(m, s)
        if m is not None and (best is None or m > best[1]):
            best = (tcid, m)
    L = OVEN[r.oven_id]
    smin = round(L * 60 / MAX_DWELL, 2)
    smax = round(L * 60 / MIN_DWELL[r.board_family], 2)
    act = round(float(r.conveyor_speed_cm_min), 2)
    ramp = None if best is None else round(best[1], 2)
    runs.append({
        'run_id': r.run_id,
        'tc_id': None if best is None else best[0],
        'max_preheat_ramp_c_per_s': ramp,
        'ramp_ok': bool(ramp is not None and ramp <= LIMIT),
        'speed_min_cm_min': smin,
        'speed_max_cm_min': smax,
        'actual_speed_cm_min': act,
        'speed_ok': bool(smin <= act <= smax),
    })
with open(f'{W}/output/ramp_conveyor.json', 'w') as f:
    json.dump({'ramp_limit_c_per_s': LIMIT, 'runs': runs}, f, indent=2)
EOF
python3 /tmp/solve_ramp.py
