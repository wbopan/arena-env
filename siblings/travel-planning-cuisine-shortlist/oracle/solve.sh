#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_meals.py <<'EOF'
import csv

STATE = "Ohio"
CUISINES = ["American", "Chinese", "Italian", "Mediterranean"]
cities = set()
with open("cities.txt") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 2 and parts[0].strip() == STATE:
            cities.add(parts[1].strip())
with open("restaurants.csv", newline="") as f:
    rest = list(csv.DictReader(f))
with open("meal_options.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["city", "cuisine", "restaurant", "average_cost", "aggregate_rating"])
    for c in sorted(cities):
        for cu in sorted(CUISINES):
            cands = []
            for r in rest:
                entries = [x.strip() for x in r["Cuisines"].split(",")]
                if r["City"] == c and cu in entries and int(r["Average Cost"]) <= 60:
                    cands.append((-float(r["Aggregate Rating"]), int(r["Average Cost"]), r["Name"]))
            if cands:
                nr, cost, name = min(cands)
                w.writerow([c, cu, name, cost, f"{-nr:.1f}"])
            else:
                w.writerow([c, cu, "-", 0, "0.0"])
EOF
python3 /tmp/solve_meals.py
