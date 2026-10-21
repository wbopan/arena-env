#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_trip.py <<'EOF'
import csv
import itertools
import json

STATE = "Ohio"
ORIGIN = "Minneapolis"
cities = set()
with open("cities.txt") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 2 and parts[0].strip() == STATE:
            cities.add(parts[1].strip())
best = {}
with open("accommodations.csv", newline="") as f:
    for r in csv.DictReader(f):
        if (r["city"] in cities and "No pets" not in r["house_rules"]
                and int(r["maximum occupancy"]) >= 2 and int(r["minimum nights"]) <= 2):
            p = int(r["price"])
            if r["city"] not in best or p < best[r["city"]][0]:
                best[r["city"]] = (p, r["NAME"])
with open("distance.csv", newline="") as f:
    legs = {(r["origin"], r["destination"]): int(r["cost"]) for r in csv.DictReader(f)}
sol = None
for perm in itertools.permutations(sorted(best), 3):
    rt = [ORIGIN, *perm, ORIGIN]
    hops = list(zip(rt, rt[1:]))
    if not all(h in legs for h in hops):
        continue
    drive = sum(legs[h] for h in hops)
    accc = sum(2 * best[c][0] for c in perm)
    if sol is None or drive + accc < sol[0]:
        sol = (drive + accc, rt, drive, accc)
total, rt, drive, accc = sol
out = {"route": rt, "accommodations": [best[c][1] for c in rt[1:4]],
       "driving_cost": drive, "accommodation_cost": accc, "total_cost": total}
with open("trip.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve_trip.py
