#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_motor.py <<'EOF'
import numpy as np
import pandas as pd
import yaml

with open('/root/work/system_params.yaml') as f:
    p = yaml.safe_load(f)
cT, cQ, d = float(p['cT']), float(p['cQ']), float(p['arm_length'])
lo, hi = float(p['rpm_min']), float(p['rpm_max'])
A = np.array([[cT, cT, cT, cT],
              [0, d * cT, 0, -d * cT],
              [-d * cT, 0, d * cT, 0],
              [-cQ, cQ, -cQ, cQ]], dtype=float)
cmd = pd.read_csv('/root/work/commands.csv').sort_values('id')
lines = ['id,rpm1,rpm2,rpm3,rpm4,F_act,Mx_act,My_act,Mz_act,saturated']
for _, r in cmd.iterrows():
    s = np.linalg.solve(A, np.array([r['F'], r['Mx'], r['My'], r['Mz']], dtype=float))
    raw = np.sqrt(np.clip(s, 0, None))
    rpm = np.clip(raw, lo, hi)
    fm = A @ rpm ** 2
    sat = int(((raw < lo) | (raw > hi)).any())
    lines.append('%d,' % int(r['id']) + ','.join('%.3f' % v for v in rpm) + ',' + ','.join('%.6f' % v for v in fm) + ',%d' % sat)
with open('/root/work/motor_output.csv', 'w') as f:
    f.write('\n'.join(lines) + '\n')
EOF
python3 /tmp/solve_motor.py
