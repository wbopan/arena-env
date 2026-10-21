#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
import openpyxl
wb = openpyxl.load_workbook("budget_incomplete.xlsx")
b, y, s = wb["Budget"], wb["YoY (%)"], wb["Summary"]
N = 0
while b.cell(row=N + 2, column=1).value not in (None, ""):
    N += 1
V, ref = {}, {}
for i in range(N):
    for k in range(6):
        V[("B", i, k)] = b.cell(row=i + 2, column=k + 2).value
        ref[("B", i, k)] = f"Budget!{b.cell(row=i + 2, column=k + 2).coordinate}"
    for k in range(1, 6):
        V[("Y", i, k)] = y.cell(row=i + 2, column=k + 1).value
        ref[("Y", i, k)] = f"YoY (%)!{y.cell(row=i + 2, column=k + 1).coordinate}"
    V[("C", i, 0)] = s.cell(row=i + 2, column=2).value
    ref[("C", i, 0)] = f"Summary!B{i + 2}"
    V[("A", i, 0)] = s.cell(row=i + 2, column=3).value
    ref[("A", i, 0)] = f"Summary!C{i + 2}"
miss = {c for c, v in V.items() if v == "???"}
orig = sorted(miss)
ok = lambda c: c not in miss
def solve(c):
    t, i, k = c
    if t == "B":
        if k > 0 and ok(("B", i, k - 1)) and ok(("Y", i, k)):
            return round(V[("B", i, k - 1)] * (1 + V[("Y", i, k)] / 100))
        if k < 5 and ok(("B", i, k + 1)) and ok(("Y", i, k + 1)):
            return round(V[("B", i, k + 1)] / (1 + V[("Y", i, k + 1)] / 100))
        if k == 0 and ok(("B", i, 5)) and ok(("C", i, 0)):
            return round(V[("B", i, 5)] / (1 + V[("C", i, 0)] / 100) ** 5)
        if k == 5 and ok(("B", i, 0)) and ok(("C", i, 0)):
            return round(V[("B", i, 0)] * (1 + V[("C", i, 0)] / 100) ** 5)
        if ok(("A", i, 0)) and all(ok(("B", i, j)) for j in range(6) if j != k):
            return round(6 * V[("A", i, 0)] - sum(V[("B", i, j)] for j in range(6) if j != k))
        return None
    if t == "Y":
        if ok(("B", i, k)) and ok(("B", i, k - 1)):
            return (V[("B", i, k)] / V[("B", i, k - 1)] - 1) * 100
        return None
    if t == "C":
        if ok(("B", i, 0)) and ok(("B", i, 5)):
            return ((V[("B", i, 5)] / V[("B", i, 0)]) ** 0.2 - 1) * 100
        return None
    if all(ok(("B", i, j)) for j in range(6)):
        return sum(V[("B", i, j)] for j in range(6)) / 6
    return None
while miss:
    for c in sorted(miss):
        v = solve(c)
        if v is not None:
            V[c] = v
            miss.discard(c)
out = {}
for c in orig:
    out[ref[c]] = int(V[c]) if c[0] == "B" else round(V[c], 2)
with open("recovered.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve.py
