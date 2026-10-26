#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_coincidence.py <<'PY'
import csv
import math
import yaml

root = '/root/work/'
def read(name):
    with open(root + name, newline='') as f:
        return list(csv.DictReader(f))

pairs = []
for h in read('hanford_triggers.csv'):
    for l in read('livingston_triggers.csv'):
        dt = float(l['time_s']) - float(h['time_s'])
        m1, m2 = float(h['total_mass_solar']), float(l['total_mass_solar'])
        if abs(dt) <= .012 and abs(m1-m2) <= 2.0:
            rho2 = float(h['snr'])**2 + float(l['snr'])**2
            pairs.append((-rho2, h['trigger_id'], l['trigger_id'], dt, (m1+m2)/2))
score, hid, lid, dt, mass = min(pairs)
answer = {'hanford_id': hid, 'livingston_id': lid,
          'network_snr': round(math.sqrt(-score), 3),
          'delay_ms': round(dt*1000, 3),
          'mean_total_mass_solar': round(mass, 3)}
with open(root + 'best_coincidence.yaml', 'w') as f:
    yaml.safe_dump(answer, f, sort_keys=False)
PY
python /tmp/solve_coincidence.py
