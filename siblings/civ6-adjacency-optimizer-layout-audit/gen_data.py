import json
import random

random.seed(1337)
W, H = 14, 10
STRAT = {"IRON", "COAL"}
LUX = {"SILK"}


def cube(x, y):
    cx = x - (y - (y & 1)) // 2
    return cx, -cx - y, y


def dist(p, q):
    a, b = cube(*p), cube(*q)
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) // 2


tiles = []
for y in range(H):
    for x in range(W):
        r = random.random()
        if r < 0.15:
            terrain = "MOUNTAIN"
        elif r < 0.27:
            terrain = "COAST"
        elif r < 0.65:
            terrain = "GRASS"
        else:
            terrain = "PLAINS"
        feature = resource = improvement = None
        if terrain == "COAST":
            if random.random() < 0.3:
                feature = "REEF"
            if random.random() < 0.2:
                resource = "FISH"
        elif terrain != "MOUNTAIN":
            f = random.random()
            if f < 0.22:
                feature = "WOODS"
            elif f < 0.38:
                feature = "RAINFOREST"
            elif f < 0.44:
                feature = "GEOTHERMAL_FISSURE"
            if feature != "GEOTHERMAL_FISSURE":
                q = random.random()
                if q < 0.05:
                    resource = "IRON"
                elif q < 0.09:
                    resource = "COAL"
                elif q < 0.13:
                    resource = "SILK"
                elif q < 0.2:
                    resource = "WHEAT"
            if feature == "WOODS" and random.random() < 0.4:
                improvement = "LUMBER_MILL"
            elif feature is None:
                q = random.random()
                if q < 0.2:
                    improvement = "MINE"
                elif q < 0.32:
                    improvement = "QUARRY"
        tiles.append({"x": x, "y": y, "terrain": terrain, "feature": feature,
                      "resource": resource, "improvement": improvement})

grid = {(t["x"], t["y"]): t for t in tiles}


def valid(t):
    return (t["terrain"] in ("GRASS", "PLAINS") and t["feature"] != "GEOTHERMAL_FISSURE"
            and t["resource"] not in STRAT | LUX)


layouts = []
lid = 1
cands = sorted(p for p, t in grid.items() if 2 <= p[0] <= W - 3 and 2 <= p[1] <= H - 3 and valid(t))
while len(layouts) < 6:
    c = random.choice(cands)
    near = sorted(p for p, t in grid.items() if p != c and 1 <= dist(p, c) <= 2 and valid(t))
    if len(near) < 3:
        continue
    picks = random.sample(near, 3)
    layouts.append({"id": "L%d" % lid, "city_center": list(c),
                    "districts": {"CAMPUS": list(picks[0]), "HOLY_SITE": list(picks[1]),
                                  "INDUSTRIAL_ZONE": list(picks[2])}})
    lid += 1

with open("map.json", "w") as f:
    json.dump({"width": W, "height": H, "tiles": tiles}, f, separators=(",", ":"))
with open("layouts.json", "w") as f:
    json.dump(layouts, f, indent=1)
