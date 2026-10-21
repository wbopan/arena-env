#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import re
from pypdf import PdfReader
from openpyxl import load_workbook, Workbook

old = {}
for page in PdfReader("price_list_backup.pdf").pages:
    for line in page.extract_text().splitlines():
        line = line.strip()
        if re.match(r"^SKU-\d{4}\s*\|", line):
            p = [x.strip() for x in line.split("|")]
            old[p[0]] = round(float(p[2].replace(",", "")), 2)
ws = load_workbook("price_list_current.xlsx", data_only=True)["Prices"]
rows = list(ws.iter_rows(values_only=True))
h = list(rows[0])
si, pi = h.index("SKU"), h.index("Unit Price")
new = {str(r[si]).strip(): round(float(r[pi]), 2) for r in rows[1:] if r[si] is not None}
out = Workbook()
o = out.active
o.title = "Changes"
o.append(["SKU", "Status", "Old Price", "New Price", "Change Pct"])
for s in sorted(set(old) | set(new)):
    if s not in new:
        o.append([s, "REMOVED", old[s], None, None])
    elif s not in old:
        o.append([s, "ADDED", None, new[s], None])
    elif old[s] != new[s]:
        o.append([s, "CHANGED", old[s], new[s], round((new[s] - old[s]) / old[s] * 100, 2)])
out.save("price_changes.xlsx")
EOF
python3 /tmp/solve.py
