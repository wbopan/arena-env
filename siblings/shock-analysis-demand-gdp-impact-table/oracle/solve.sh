#!/bin/bash
set -e
cat > /tmp/solve.py << 'EOF'
import json
import openpyxl

ws = openpyxl.load_workbook("/root/work/weo.xlsx", data_only=True)["WEO_Data"]
d = {int(r[0]): r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None}
p = json.load(open("/root/work/params.json"))
L = max(y for y in d if d[y][1] is not None and d[y][3] is not None)
g = sum(d[t][3] / d[t - 1][3] - 1 for t in range(L - 3, L + 1)) / 4
D = d[L][3]
R = d[L][1] / D * 100
w = p["allocation_weights"]
sw = sum(w)
s = p["start_year"]
wb = openpyxl.Workbook()
o = wb.active
o.title = "Impact"
o.append(["Year", "Deflator", "Real_GDP", "Investment_GEL", "Real_Investment", "GDP_Impact", "Impact_pct"])
for t in range(L + 1, s + len(w)):
    D *= 1 + g
    R *= 1 + d[t][2] / 100
    if t >= s:
        inv = p["total_investment_usd_bn"] * p["fx_gel_per_usd"] * w[t - s] / sw
        ri = inv / D * 100
        im = ri * (1 - p["import_content_share"]) * p["demand_multiplier"]
        o.append([t, D, R, inv, ri, im, im / R * 100])
wb.save("/root/work/shock_impact.xlsx")
EOF
python3 /tmp/solve.py
