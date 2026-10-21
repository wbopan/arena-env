#!/bin/bash
set -e
mkdir -p /root/work/output
cat > /tmp/solve_tal.py <<'EOF'
import csv
import pandas as pd
import yaml

W = '/root/work'
spec = yaml.safe_load(open(f'{W}/spec.yaml'))
al = {a['name']: a for a in spec['alloys']}
mes = pd.read_csv(f'{W}/mes_log.csv', dtype={'run_id': str}).sort_values('run_id')
tc = pd.read_csv(f'{W}/thermocouples.csv', dtype={'run_id': str, 'tc_id': str})

def tal(t, y, thr):
    tot = 0.0
    for i in range(1, len(t)):
        t0, t1, y0, y1 = t[i-1], t[i], y[i-1], y[i]
        if t1 <= t0:
            continue
        if y0 > thr and y1 > thr:
            tot += t1 - t0
        elif y0 <= thr < y1:
            tot += t1 - (t0 + (thr - y0) / (y1 - y0) * (t1 - t0))
        elif y1 <= thr < y0:
            tot += (t0 + (thr - y0) / (y1 - y0) * (t1 - t0)) - t0
    return tot

with open(f'{W}/output/tal_report.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['run_id', 'alloy', 'liquidus_c', 'tc_id', 'tal_s', 'tal_min_s', 'tal_max_s', 'status'])
    for _, r in mes.iterrows():
        a = al[r.alloy]
        L = float(a['liquidus_c'])
        g = tc[tc.run_id == r.run_id]
        best = None
        for tcid in sorted(g.tc_id.unique()):
            h = g[g.tc_id == tcid].sort_values('time_s', kind='mergesort')
            v = tal(h.time_s.to_numpy(float), h.temp_c.to_numpy(float), L)
            if best is None or v < best[1]:
                best = (tcid, v)
        if best is None:
            w.writerow([r.run_id, r.alloy, L, '', '', a['tal_min_s'], a['tal_max_s'], 'non-compliant'])
        else:
            v = round(best[1], 2)
            st = 'compliant' if a['tal_min_s'] <= v <= a['tal_max_s'] else 'non-compliant'
            w.writerow([r.run_id, r.alloy, L, best[0], f'{v:.2f}', a['tal_min_s'], a['tal_max_s'], st])
EOF
python3 /tmp/solve_tal.py
