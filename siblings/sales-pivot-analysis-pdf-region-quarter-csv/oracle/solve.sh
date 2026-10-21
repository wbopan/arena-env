#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import re
from openpyxl import load_workbook
from pypdf import PdfReader

ws = load_workbook("/root/work/stores.xlsx")["Stores"]
rows = list(ws.iter_rows(values_only=True))
h = list(rows[0])
smap = {r[h.index("StoreID")]: r[h.index("Region")] for r in rows[1:] if r[0]}

text = "\n".join(p.extract_text() or "" for p in PdfReader("/root/work/transactions.pdf").pages)
pat = re.compile(r"\d{4}-(\d{2})-\d{2}\s+(S\d{2})\s+[A-Za-z]+\s+(-?\d+\.\d{2})")
m = {r: [0.0] * 4 for r in set(smap.values())}
for mo, st, amt in pat.findall(text):
    m[smap[st]][(int(mo) - 1) // 3] += float(amt)

lines = ["Region,Q1,Q2,Q3,Q4,Total"]
gt = [0.0] * 5
for reg in sorted(m):
    vals = [round(v, 2) for v in m[reg]] + [round(sum(m[reg]), 2)]
    gt = [a + b for a, b in zip(gt, vals)]
    lines.append(reg + "," + ",".join(f"{v:.2f}" for v in vals))
lines.append("Grand Total," + ",".join(f"{v:.2f}" for v in gt))
with open("/root/work/region_quarter.csv", "w") as f:
    f.write("\n".join(lines) + "\n")
EOF
python3 /tmp/solve.py
