#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv
TAB = chr(9)

def read(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f, delimiter=TAB))

names = {r["ACCESSION_NUMBER"]: r["FILINGMANAGER_NAME"].strip() for r in read("2025-q3/COVERPAGE.tsv")}
info = read("2025-q3/INFOTABLE.tsv")
cusip = [r["CUSIP"] for r in info if "palantir" in r["NAMEOFISSUER"].lower()][0]
total, pos = {}, {}
for r in info:
    a, v = r["ACCESSION_NUMBER"], int(r["VALUE"])
    total[a] = total.get(a, 0) + v
    if r["CUSIP"] == cusip and r["SSHPRNAMTTYPE"] == "SH" and r["PUTCALL"].strip() == "":
        pos[a] = pos.get(a, 0) + v
ranked = sorted([a for a in pos if pos[a] > 0], key=lambda a: (-pos[a], a))[:5]
with open("top_holders.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rank", "manager_name", "accession_number", "value", "pct_of_portfolio"])
    for i, a in enumerate(ranked):
        w.writerow([i + 1, names[a], a, pos[a], f"{100 * pos[a] / total[a]:.2f}"])
EOF
python3 /tmp/solve.py
