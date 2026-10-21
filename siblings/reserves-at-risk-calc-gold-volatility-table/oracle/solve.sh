#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import math, statistics
from openpyxl import load_workbook, Workbook
ws = load_workbook('gold_prices.xlsx', data_only=True)['Prices']
rows = [(str(r[0]).strip(), float(r[1])) for r in ws.iter_rows(min_row=4, values_only=True) if r[0] is not None]
ret = [None] + [100 * math.log(rows[i][1] / rows[i-1][1]) for i in range(1, len(rows))]
wb = Workbook(); o = wb.active; o.title = 'Volatility'
o.append(['Period', 'Price', 'LogReturn', 'Vol3M', 'Vol12M', 'Vol3M_Ann'])
for i, (per, pr) in enumerate(rows):
    v3 = statistics.stdev(ret[i-2:i+1]) if i >= 3 else None
    v12 = statistics.stdev(ret[i-11:i+1]) if i >= 12 else None
    o.append([per, pr,
              None if ret[i] is None else round(ret[i], 6),
              None if v3 is None else round(v3, 6),
              None if v12 is None else round(v12, 6),
              None if v3 is None else round(v3 * math.sqrt(12), 6)])
wb.save('gold_vol.xlsx')
EOF
python3 /tmp/solve.py
