#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
from openpyxl import load_workbook

ws = load_workbook('/root/work/data.xlsx', data_only=True)['Trades']
tiers = [(200000, 0.0008), (50000, 0.0012), (10000, 0.002), (0, 0.003)]
agg = {}
for tid, client, side, q, p in ws.iter_rows(min_row=2, values_only=True):
    if tid is None:
        continue
    n = round(float(q) * float(p), 2)
    rate = next(r for lo, r in tiers if n >= lo)
    charge = max(n * rate, 7.5)
    if str(side).upper() == 'SELL':
        charge += n * 0.000025
    c, t = agg.get(client, (0, 0.0))
    agg[client] = (c + 1, t + round(charge, 2))

with open('/root/work/commissions.csv', 'w') as f:
    f.write('client,trades,total_charges\n')
    for k in sorted(agg):
        f.write(f'{k},{agg[k][0]},{agg[k][1]:.2f}\n')
EOF
python3 /tmp/solve.py
