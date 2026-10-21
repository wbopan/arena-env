#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import openpyxl
wb = openpyxl.load_workbook("sales_incomplete.xlsx")
ws = wb["Quarterly Sales"]
miss = {(r, c) for r in range(2, 11) for c in range(2, 7) if ws.cell(row=r, column=c).value == "???"}
cons = [([(r, c) for c in range(2, 6)], (r, 6)) for r in range(2, 11)]
cons += [([(r, c) for r in range(2, 10)], (10, c)) for c in range(2, 7)]
while miss:
    for parts, tot in cons:
        m = [x for x in parts + [tot] if x in miss]
        if len(m) == 1:
            x = m[0]
            s = sum(ws.cell(row=p[0], column=p[1]).value for p in parts if p != x)
            v = s if x == tot else ws.cell(row=tot[0], column=tot[1]).value - s
            ws.cell(row=x[0], column=x[1]).value = int(v)
            miss.discard(x)
wb.save("sales_recovered.xlsx")
EOF
python3 /tmp/solve.py
