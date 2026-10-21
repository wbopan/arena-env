#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_metrics.py << 'EOF'
import json
import pandas as pd
import yaml

cfg = yaml.safe_load(open('sim_config.yaml'))
a = cfg['acc_settings']
s = float(a['set_speed']); th = float(a['time_headway']); md = float(a['min_distance'])
dt = float(cfg['simulation']['dt'])
df = pd.read_csv('drive_log.csv')
lead = df['lead_speed'].notna()
first = int(lead.to_numpy().argmax())
cr = df.iloc[:first]
t10 = cr.loc[cr['ego_speed'] >= 0.1 * s, 'time'].iloc[0]
t90 = cr.loc[cr['ego_speed'] >= 0.9 * s, 'time'].iloc[0]
ov = max(0.0, (cr['ego_speed'].max() - s) / s * 100.0)
sse = abs(s - cr['ego_speed'].iloc[-25:].mean())
tail = df.iloc[-50:]
dse = abs((tail['distance'] - (md + th * tail['ego_speed'])).mean())
ld = df[lead]
rel = ld['ego_speed'] - ld['lead_speed']
m = rel > 0
ttc = round(float((ld['distance'][m] / rel[m]).min()), 3) if m.any() else None
res = {
    'rise_time_s': round(float(t90 - t10), 3),
    'overshoot_pct': round(float(ov), 3),
    'speed_ss_error': round(float(sse), 3),
    'distance_ss_error': round(float(dse), 3),
    'min_distance_m': round(float(ld['distance'].min()), 3),
    'min_ttc_s': ttc,
    'follow_duration_s': round(len(ld) * dt, 3),
}
json.dump(res, open('metrics.json', 'w'), indent=2)
EOF
python3 /tmp/solve_metrics.py
