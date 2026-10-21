#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, json, math
CONV = {
    "Creatinine": {"mg/dl": 1.0, "umol/l": 1 / 88.4},
    "BUN": {"mg/dl": 1.0, "mmol/l": 2.8},
    "Hemoglobin": {"g/dl": 1.0, "g/l": 0.1, "mmol/l": 1.611},
    "Calcium": {"mg/dl": 1.0, "mmol/l": 4.0, "meq/l": 2.0},
    "Glucose": {"mg/dl": 1.0, "mmol/l": 18.016},
    "Albumin": {"g/dl": 1.0, "g/l": 0.1},
}
dropped = 0
vals = {a: [] for a in CONV}
with open("measurements.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        a = r["analyte"].strip()
        u = r["unit"].strip().lower().replace("\u00b5", "u").replace("\u03bc", "u")
        try:
            v = float(r["value"].strip().replace(",", "."))
        except ValueError:
            v = None
        if v is None or not math.isfinite(v) or a not in CONV or u not in CONV[a]:
            dropped += 1
            continue
        vals[a].append(v * CONV[a][u])
out = {"dropped_rows": dropped, "analytes": {}}
for a, x in vals.items():
    out["analytes"][a] = {"n": len(x), "mean": round(sum(x) / len(x), 2),
                          "min": round(min(x), 2), "max": round(max(x), 2)}
with open("lab_summary.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve.py
