import json
import random

random.seed(2024)
W, H = 14, 10

tiles = []
for y in range(H):
    for x in range(W):
        r = random.random()
        if r < 0.16:
            terrain = "MOUNTAIN"
        elif r < 0.30:
            terrain = "COAST"
        elif r < 0.65:
            terrain = "GRASS"
        else:
            terrain = "PLAINS"
        feature = resource = None
        if terrain == "COAST":
            if random.random() < 0.35:
                feature = "REEF"
            if random.random() < 0.2:
                resource = "FISH"
        elif terrain != "MOUNTAIN":
            f = random.random()
            if f < 0.2:
                feature = "WOODS"
            elif f < 0.38:
                feature = "RAINFOREST"
            elif f < 0.47:
                feature = "GEOTHERMAL_FISSURE"
            if feature != "GEOTHERMAL_FISSURE":
                q = random.random()
                if q < 0.05:
                    resource = "IRON"
                elif q < 0.08:
                    resource = "NITER"
                elif q < 0.12:
                    resource = "SILK"
                elif q < 0.15:
                    resource = "WINE"
                elif q < 0.22:
                    resource = "WHEAT"
        tiles.append({"x": x, "y": y, "terrain": terrain, "feature": feature, "resource": resource})

cands = [(t["x"], t["y"]) for t in tiles
         if 3 <= t["x"] <= W - 4 and 3 <= t["y"] <= H - 4
         and t["terrain"] in ("GRASS", "PLAINS") and t["feature"] is None and t["resource"] is None]
center = random.choice(sorted(cands))

with open("map.json", "w") as f:
    json.dump({"width": W, "height": H, "tiles": tiles}, f, separators=(",", ":"))
with open("city.json", "w") as f:
    json.dump({"city_center": list(center)}, f)
