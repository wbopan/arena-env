#!/bin/bash
set -e
cat > /tmp/solve.py << 'EOF'
import json
import openpyxl

wb = openpyxl.load_workbook("/root/work/sut.xlsx", data_only=True)

def rows(ws):
    d = {}
    for r in ws.iter_rows(min_row=4, values_only=True):
        if r[0] is None or str(r[0]).strip().upper() == "TOTAL":
            continue
        d[str(r[0]).strip()] = r
    return d

s = rows(wb["SUPPLY"])
u = rows(wb["USE"])
rat = {c: s[c][3] / s[c][6] for c in s}
gf = {c: float(u[c][5] or 0) for c in u}
tot = sum(gf.values())
share = sum(gf[c] * rat[c] for c in gf) / tot
top = max(gf, key=lambda c: gf[c] * rat[c])
res = {"import_content_share": round(share, 6), "gfcf_total": round(tot, 1), "top_import_contributor": top, "import_ratios": {c: round(v, 6) for c, v in rat.items()}}
with open("/root/work/import_content.json", "w") as f:
    json.dump(res, f, indent=2)
EOF
python3 /tmp/solve.py
