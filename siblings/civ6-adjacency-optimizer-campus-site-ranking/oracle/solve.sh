#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_sites.py <<'EOF'
import json

BLOCK = {"IRON", "COAL", "HORSES", "NITER", "OIL", "ALUMINUM", "URANIUM", "SILK", "WINE", "DIAMONDS"}

def nbrs(x, y):
    if y % 2 == 0:
        d = [(1, 0), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
    else:
        d = [(1, 0), (1, -1), (0, -1), (-1, 0), (0, 1), (1, 1)]
    return [(x + a, y + b) for a, b in d]

def cube(x, y):
    cx = x - (y - (y & 1)) // 2
    return (cx, -cx - y, y)

def hd(p, q):
    a, b = cube(*p), cube(*q)
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) // 2

m = json.load(open("map.json"))
c = tuple(json.load(open("city.json"))["city_center"])
grid = {(t["x"], t["y"]): t for t in m["tiles"]}
rows = []
for p, t in grid.items():
    d = hd(p, c)
    if d < 1 or d > 3:
        continue
    if t["terrain"] not in ("GRASS", "PLAINS") or t["feature"] == "GEOTHERMAL_FISSURE" or t["resource"] in BLOCK:
        continue
    cnt = {"GEOTHERMAL_FISSURE": 0, "REEF": 0, "RAINFOREST": 0, "WOODS": 0, "MTN": 0, "DIST": 0}
    for q in nbrs(*p):
        n = grid.get(q)
        if n is None:
            continue
        f = n["feature"]
        if q == c:
            cnt["DIST"] += 1
            if f in ("WOODS", "RAINFOREST"):
                f = None
        if n["terrain"] == "MOUNTAIN":
            cnt["MTN"] += 1
        if f in cnt:
            cnt[f] += 1
    campus = 2 * cnt["GEOTHERMAL_FISSURE"] + 2 * cnt["REEF"] + cnt["MTN"] + cnt["RAINFOREST"] // 2 + cnt["DIST"] // 2
    holy = cnt["MTN"] + cnt["WOODS"] // 2 + cnt["DIST"] // 2
    rows.append((p[0], p[1], d, campus, holy))
rows.sort(key=lambda r: (-r[3], -r[4], r[1], r[0]))
with open("campus_sites.csv", "w") as f:
    f.write("x,y,distance,campus,holy_site\n")
    for r in rows:
        f.write(",".join(str(v) for v in r) + "\n")
EOF
python3 /tmp/solve_sites.py
