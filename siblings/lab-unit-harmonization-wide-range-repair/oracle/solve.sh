#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv
ref = {}
with open("lab_reference.csv", newline="") as f:
    for r in csv.DictReader(f):
        ref[r["feature"]] = (float(r["min"]), float(r["max"]),
                             [float(x) for x in r["alt_factors"].split(";") if x.strip()])

def parse(s):
    s = s.strip()
    if s.lower() in ("", "na", "nan"):
        return None
    return float(s.replace(",", "."))

with open("labs_wide.csv", newline="") as f:
    rows = list(csv.reader(f))
header, data = rows[0], rows[1:]
out = [header]
for r in data:
    vals = [parse(c) for c in r[1:]]
    if any(v is None for v in vals):
        continue
    res = [r[0].strip()]
    for col, v in zip(header[1:], vals):
        lo, hi, facs = ref[col]
        if not (lo <= v <= hi):
            for k in facs:
                if lo <= v * k <= hi:
                    v = v * k
                    break
        res.append(f"{v:.2f}")
    out.append(res)
with open("harmonized.csv", "w", newline="") as f:
    csv.writer(f).writerows(out)
EOF
python3 /tmp/solve.py
