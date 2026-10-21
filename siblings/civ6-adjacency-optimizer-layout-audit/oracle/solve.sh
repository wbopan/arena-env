#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_adj.py <<'EOF'
import json

STRAT = {"IRON", "COAL", "HORSES", "NITER", "OIL", "ALUMINUM", "URANIUM"}

def nbrs(x, y):
    if y % 2 == 0:
        d = [(1, 0), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]
    else:
        d = [(1, 0), (1, -1), (0, -1), (-1, 0), (0, 1), (1, 1)]
    return [(x + a, y + b) for a, b in d]

m = json.load(open("map.json"))
layouts = json.load(open("layouts.json"))
grid = {(t["x"], t["y"]): t for t in m["tiles"]}
out = []
grand = 0
for L in layouts:
    occ = {tuple(L["city_center"])} | {tuple(v) for v in L["districts"].values()}
    bon = {}
    for d, p in L["districts"].items():
        cnt = {}
        def add(k):
            cnt[k] = cnt.get(k, 0) + 1
        for q in nbrs(*p):
            t = grid.get(q)
            if t is None:
                continue
            o = q in occ
            if o:
                add("DIST")
            if t["terrain"] == "MOUNTAIN":
                add("MTN")
            f = t["feature"]
            if f and not (o and f in ("WOODS", "RAINFOREST")):
                add(f)
            if t["improvement"] and not o:
                add(t["improvement"])
            if t["resource"] in STRAT:
                add("STRAT")
        g = lambda k: cnt.get(k, 0)
        if d == "CAMPUS":
            v = 2 * g("GEOTHERMAL_FISSURE") + 2 * g("REEF") + g("MTN") + g("RAINFOREST") // 2 + g("DIST") // 2
        elif d == "HOLY_SITE":
            v = g("MTN") + g("WOODS") // 2 + g("DIST") // 2
        else:
            v = g("QUARRY") + g("STRAT") + g("MINE") // 2 + g("LUMBER_MILL") // 2 + g("DIST") // 2
        bon[d] = v
    tot = sum(bon.values())
    grand += tot
    out.append({"id": L["id"], "bonuses": bon, "total": tot})
json.dump({"layouts": out, "grand_total": grand}, open("adjacency.json", "w"), indent=2)
EOF
python3 /tmp/solve_adj.py
