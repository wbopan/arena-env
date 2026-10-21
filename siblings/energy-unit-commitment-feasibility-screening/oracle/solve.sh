#!/bin/bash
set -e
cd /root/work
cat > /tmp/screen.py <<'EOF'
import csv
import json

case = json.load(open('case.json'))
cands = json.load(open('candidates.json'))['schedules']
T = case['time_periods']
G = case['thermal_generators']
E = 1e-6
rows = []
for s in cands:
    U, P = s['commitment'], s['production_MW']
    ok = {k: True for k in ['demand_balance', 'generator_limits', 'spinning_reserve', 'ramping', 'minimum_up_down']}
    for t in range(T):
        if abs(sum(P[n][t] for n in G) - case['demand'][t]) > 0.01:
            ok['demand_balance'] = False
        head = sum(G[n]['power_output_maximum'] - P[n][t] for n in G if U[n][t] == 1)
        if head < case['reserves'][t] - 0.01:
            ok['spinning_reserve'] = False
    for n, g in G.items():
        st = [g['unit_on_t0']] + list(U[n])
        pr = [g['power_output_t0']] + list(P[n])
        for k in range(1, T + 1):
            if st[k] == 1:
                if not (g['power_output_minimum'] - E <= pr[k] <= g['power_output_maximum'] + E):
                    ok['generator_limits'] = False
                if st[k - 1] == 1:
                    d = pr[k] - pr[k - 1]
                    if d > g['ramp_up_limit'] + E or -d > g['ramp_down_limit'] + E:
                        ok['ramping'] = False
            elif st[k] != 0 or abs(pr[k]) > E:
                ok['generator_limits'] = False
            if st[k] != st[k - 1]:
                L = g['time_up_minimum'] if st[k] == 1 else g['time_down_minimum']
                if any(x != st[k] for x in st[k:min(T + 1, k + L)]):
                    ok['minimum_up_down'] = False
        if g['unit_on_t0'] == 1:
            rem = g['time_up_minimum'] - g['time_up_t0']
        else:
            rem = g['time_down_minimum'] - g['time_down_t0']
        if rem > 0 and any(x != g['unit_on_t0'] for x in st[1:1 + rem]):
            ok['minimum_up_down'] = False
    vals = list(ok.values())
    rows.append([s['id']] + ['pass' if v else 'fail' for v in vals] + ['pass' if all(vals) else 'fail'])

with open('checks.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['schedule'] + list(ok.keys()) + ['overall'])
    w.writerows(rows)
EOF
python3 /tmp/screen.py
