#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import math
import openpyxl
wb = openpyxl.load_workbook('shock_inputs.xlsx', data_only=True)
b = sorted([r for r in wb['Baseline'].iter_rows(min_row=2, values_only=True) if r[0] is not None], key=lambda r: int(r[0]))
inv = {int(r[0]): float(r[1]) for r in wb['Investment'].iter_rows(min_row=2, values_only=True) if r[0] is not None}
prm = {str(r[0]).strip(): float(r[1]) for r in wb['Params'].iter_rows(min_row=2, values_only=True) if r[0] is not None}
a, d = prm['alpha'], prm['delta']
out = openpyxl.Workbook()
ws = out.active
ws.title = 'Shock'
ws.append(['year', 'I', 'dK', 'K_with', 'Ystar_base', 'Ystar_with', 'gap_pct'])
dk = 0.0
for yr, kb, z in b:
    i = inv.get(int(yr), 0.0)
    dk = (1 - d) * dk + i
    kw = kb + dk
    yb = math.exp(z) * kb ** a
    yw = math.exp(z) * kw ** a
    ws.append([int(yr), i, dk, kw, yb, yw, 100 * (yw / yb - 1)])
out.save('shock_results.xlsx')
EOF
python3 /tmp/solve.py
