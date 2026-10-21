#!/bin/bash
set -e
cat > /tmp/sta.py <<'EOF'
import glob, os, csv
import numpy as np
os.chdir('/root/work')
rows = []
for f in sorted(glob.glob('trace_*.npz')):
    d = np.load(f)
    dt = float(d['dt'])
    ch = [c.strip() for c in str(d['channels']).split(',')]
    zi = [k for k, c in enumerate(ch) if c.endswith('Z')][0]
    x = d['data'][:, zi].astype(float)
    x = x - x.mean()
    e = x * x
    ns = int(round(0.5 / dt))
    nl = int(round(5.0 / dt))
    trig = -1
    for i in range(nl - 1, len(e)):
        sta = e[i - ns + 1:i + 1].mean()
        lta = e[i - nl + 1:i + 1].mean()
        if lta > 0 and sta / lta >= 3.0:
            trig = i
            break
    t = round(trig * dt, 3) if trig >= 0 else -1
    rows.append((os.path.basename(f), trig, t))
with open('triggers.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['file_name', 'trigger_idx', 'trigger_time_s'])
    w.writerows(rows)
EOF
python3 /tmp/sta.py
