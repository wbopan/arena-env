#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
import re
from pypdf import PdfReader
from openpyxl import load_workbook

old = {}
for page in PdfReader("roster_backup.pdf").pages:
    for line in page.extract_text().splitlines():
        line = line.strip()
        if re.match(r"^EMP\d{5}\s*\|", line):
            p = [x.strip() for x in line.split("|")]
            old[p[0]] = (p[2], int(re.sub(r"\D", "", p[3])))
ws = load_workbook("roster_current.xlsx", data_only=True)["Employees"]
rows = list(ws.iter_rows(values_only=True))
h = list(rows[0])
i, j, k = h.index("Employee ID"), h.index("Department"), h.index("Annual Salary")
new = {str(r[i]).strip(): (str(r[j]).strip(), int(r[k])) for r in rows[1:] if r[i] is not None}
deps = sorted({v[0] for v in old.values()} | {v[0] for v in new.values()})
out = []
for d in deps:
    po = sum(v[1] for v in old.values() if v[0] == d)
    pn = sum(v[1] for v in new.values() if v[0] == d)
    out.append({"department": d,
                "headcount_old": sum(1 for v in old.values() if v[0] == d),
                "headcount_new": sum(1 for v in new.values() if v[0] == d),
                "payroll_old": po, "payroll_new": pn, "payroll_change": pn - po})
res = {"departments": out,
       "transfers": sum(1 for x in old if x in new and old[x][0] != new[x][0]),
       "net_headcount_change": len(new) - len(old)}
with open("dept_summary.json", "w") as f:
    json.dump(res, f, indent=2)
EOF
python3 /tmp/solve.py
