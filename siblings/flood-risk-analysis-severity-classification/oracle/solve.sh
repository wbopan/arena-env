#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import csv, json

def num(x):
    x = (x or '').strip()
    if not x:
        return None
    v = float(x)
    return None if v == -9999 else v

daily = {}
with open('gage_height_iv.rdb') as f:
    lines = [l.rstrip('\n') for l in f if not l.startswith('#') and l.strip()]
cols = lines[0].split('\t')
ci = {c: i for i, c in enumerate(cols)}
for l in lines[2:]:
    p = l.split('\t') + [''] * len(cols)
    v = p[ci['00065']].strip()
    if not v:
        continue
    s = p[ci['site_no']].strip(); d = p[ci['datetime']][:10]; v = float(v)
    dd = daily.setdefault(s, {})
    if d not in dd or v > dd[d]:
        dd[d] = v

thr = {}
with open('nws_thresholds.csv', newline='') as f:
    r = csv.reader(f); h = next(r)
    for row in r:
        m = dict(zip(h, row[:len(h)]))
        thr[m['usgs id'].strip()] = m

out = []
for s in sorted(daily):
    if s not in thr:
        continue
    t = thr[s]; fl = num(t['flood stage'])
    if fl is None:
        continue
    dd = daily[s]; peak = max(dd.values())
    pdate = min(d for d, v in dd.items() if v == peak)
    sev = 'normal'
    for name, key in [('major', 'major flood stage'), ('moderate', 'moderate flood stage'), ('minor', 'flood stage'), ('action', 'action stage')]:
        tv = num(t[key])
        if tv is not None and peak >= tv:
            sev = name; break
    out.append({'station_id': s, 'peak_stage_ft': round(peak, 2), 'peak_date': pdate, 'severity': sev, 'flood_days': sum(1 for v in dd.values() if v >= fl)})

with open('flood_severity.json', 'w') as f:
    json.dump({'stations': out}, f, indent=2)
EOF
python3 /tmp/solve.py
