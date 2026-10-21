#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import numpy as np
import pandas as pd
VP = 6.0
VS = VP / 1.75
st = pd.read_csv('stations.csv').set_index('station_id')
ev = pd.read_csv('events.csv')
pk = pd.read_csv('picks.csv')
ref = pd.Timestamp('2000-01-01')
et = (pd.to_datetime(ev['time']) - ref).dt.total_seconds().to_numpy()
pt = (pd.to_datetime(pk['timestamp']) - ref).dt.total_seconds().to_numpy()
ex = ev['x_km'].to_numpy(float)
ey = ev['y_km'].to_numpy(float)
ez = ev['z_km'].to_numpy(float)
out = []
for i in range(len(pk)):
    s = st.loc[pk['station_id'].iloc[i]]
    d = np.sqrt((ex - s['x_km']) ** 2 + (ey - s['y_km']) ** 2 + (ez + s['elevation_m'] / 1000.0) ** 2)
    v = VP if str(pk['phase'].iloc[i]).upper() == 'P' else VS
    r = np.abs(pt[i] - (et + d / v))
    j = int(np.argmin(r))
    out.append(int(ev['event_id'].iloc[j]) if r[j] <= 1.0 else -1)
pd.DataFrame({'pick_id': pk['pick_id'], 'event_id': out}).to_csv('assignments.csv', index=False)
EOF
python3 /tmp/solve.py
