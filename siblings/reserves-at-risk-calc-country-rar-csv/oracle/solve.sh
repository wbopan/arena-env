#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, math, statistics
from openpyxl import load_workbook
with open('gold_monthly.csv') as f:
    g = list(csv.DictReader(f))
pr = [float(r['price_usd_per_ozt']) for r in g]
ret = [100 * math.log(pr[i] / pr[i-1]) for i in range(1, len(pr))]
sigma = statistics.stdev(ret[-3:])
p25 = [float(r['price_usd_per_ozt']) for r in g if r['period'].startswith('2025')]
avg = sum(p25) / len(p25)
wb = load_workbook('reserves.xlsx', data_only=True)
def y25(name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    hdr = [str(h).strip() for h in rows[0]]
    ci, yi = hdr.index('Country'), hdr.index('2025')
    return {str(r[ci]).strip(): float(r[yi]) for r in rows[1:] if r[ci] is not None and r[yi] not in (None, '')}
val, vol, tot = y25('Value'), y25('Volume'), y25('Total Reserves')
gv = dict(val)
for c, v in vol.items():
    if c not in gv:
        gv[c] = v * avg
out = []
for c, v in gv.items():
    if c in tot:
        e = v * sigma / 100
        out.append((c, v, e, tot[c], e / tot[c] * 100))
out.sort(key=lambda t: -t[4])
with open('rar.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['country', 'gold_value_musd', 'exposure_musd', 'total_reserves_musd', 'rar_pct'])
    for c, v, e, t, r in out:
        w.writerow([c, round(v, 4), round(e, 4), round(t, 4), round(r, 4)])
EOF
python3 /tmp/solve.py
