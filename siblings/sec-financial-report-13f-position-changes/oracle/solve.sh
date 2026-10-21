#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, json
TAB = chr(9)

def read(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f, delimiter=TAB))

def acc(q):
    return [r["ACCESSION_NUMBER"] for r in read(q + "/COVERPAGE.tsv")
            if r["FILINGMANAGER_NAME"].strip().lower() == "berkshire hathaway inc"][0]

def hold(q, a):
    h = {}
    for r in read(q + "/INFOTABLE.tsv"):
        if r["ACCESSION_NUMBER"] == a and r["SSHPRNAMTTYPE"] == "SH" and r["PUTCALL"].strip() == "":
            h[r["CUSIP"]] = h.get(r["CUSIP"], 0) + int(r["VALUE"])
    return h

a2, a3 = acc("2025-q2"), acc("2025-q3")
h2, h3 = hold("2025-q2", a2), hold("2025-q3", a3)
d = {c: h3[c] - h2[c] for c in h3 if c in h2 and h3[c] > h2[c]}
res = {
    "q2_accession": a2, "q3_accession": a3,
    "q2_stock_value": sum(h2.values()), "q3_stock_value": sum(h3.values()),
    "new_positions": sorted([c for c in h3 if c not in h2], key=lambda c: (-h3[c], c)),
    "exited_positions": sorted([c for c in h2 if c not in h3], key=lambda c: (-h2[c], c)),
    "top_increases": sorted(d, key=lambda c: (-d[c], c))[:3],
}
with open("changes.json", "w") as f:
    json.dump(res, f, indent=2)
EOF
python3 /tmp/solve.py
