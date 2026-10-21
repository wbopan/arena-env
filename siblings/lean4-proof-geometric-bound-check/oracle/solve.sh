#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_bounds.py << 'EOF'
import csv
from fractions import Fraction as F
out = []
with open("/root/work/sequences.csv", newline="") as fh:
    for row in csv.DictReader(fh):
        s0, a, r, b = (F(row[k]) for k in ("s0", "a", "r", "bound"))
        L = s0 + a * r / (1 - r)
        holds = L <= b
        fv = ""
        if not holds:
            n, S = 0, s0
            while not S > b:
                n += 1
                S = S + a * r ** n
            fv = str(n)
        out.append([row["id"], f"{L.numerator}/{L.denominator}", "true" if holds else "false", fv])
with open("/root/work/bounds_report.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "limit", "holds", "first_violation"])
    w.writerows(out)
EOF
python3 /tmp/solve_bounds.py
