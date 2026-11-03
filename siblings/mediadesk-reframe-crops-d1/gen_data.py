import csv, json, random
random.seed(20261499)
LEVEL = 1
sizes = [(3840, 2160), (1920, 1080), (1280, 720), (4096, 1716), (1440, 1080), (2048, 858), (1080, 1920), (3000, 2000), (720, 576)]
rows = []
for i in range(random.randint(4, 7)):
    W, H = random.choice(sizes)
    if random.random() < 0.4:
        W += random.choice([-6, 2, 10, 14]); H += random.choice([-2, 6, 12])
    rows.append(["SRC%02d" % (i + 1), W, H])
with open("sources.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["source_id", "width", "height"]); w.writerows(rows)
plats = [{"name": "vertical", "aspect": "9:16", "out_width": 1080}, {"name": "square", "aspect": "1:1", "out_width": 1080},
         {"name": "feed", "aspect": "4:5", "out_width": 1080}, {"name": "wide", "aspect": "16:9", "out_width": 1920},
         {"name": "cinema", "aspect": "21:9", "out_width": 2560}]
plats = random.sample(plats, random.randint(2, 4))
if LEVEL >= 2:
    for p in plats:
        p["no_upscale"] = True
json.dump(plats, open("platforms.json", "w"), indent=1)
