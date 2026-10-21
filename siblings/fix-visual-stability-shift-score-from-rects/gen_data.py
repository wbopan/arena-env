import json
import random

random.seed(4242)
W, H = 1280, 800
frames = []
ids = list(range(1, 33))
random.shuffle(ids)
names = ["hero-banner", "promo-strip", "product-grid", "side-pane", "results-bar", "footer", "ad-slot", "review-list"]
for i in ids:
    x = random.randint(-300, 1400)
    y = random.randint(-300, 1000)
    w = random.randint(40, 900)
    h = random.randint(20, 500)
    mode = random.random()
    dx = random.randint(-400, 400) if mode < 0.5 else 0
    dy = random.randint(-600, 600) if mode > 0.3 else 0
    if dx == 0 and dy == 0:
        dy = random.randint(10, 300)
    nw = w if random.random() < 0.7 else max(10, w + random.randint(-100, 200))
    nh = h if random.random() < 0.7 else max(10, h + random.randint(-80, 150))
    if i % 11 == 0:
        dy = random.choice([1, -1]) * random.randint(1400, 1800)
    frames.append({
        "id": f"f{i:03d}",
        "element": random.choice(names),
        "previous": {"x": x, "y": y, "width": w, "height": h},
        "current": {"x": x + dx, "y": y + dy, "width": nw, "height": nh},
    })
with open("frames.json", "w") as f:
    json.dump({"viewport": {"width": W, "height": H}, "frames": frames}, f, indent=1)
