import json
import random

random.seed(1234)
pages = []
for i in range(12):
    t = random.randint(100, 800)
    entries = []
    n = random.randint(4, 14)
    for _ in range(n):
        gap = random.choice([random.randint(50, 900), random.randint(1100, 2500), random.randint(200, 700)])
        t += gap
        entries.append({
            "startTime": round(t + random.random(), 2),
            "value": round(random.uniform(0.002, 0.12), 5),
            "hadRecentInput": random.random() < 0.2,
        })
    random.shuffle(entries)
    pages.append({"url": f"/page-{i:02d}", "entries": entries})
# one page with only input-driven shifts
pages.append({"url": "/page-input-only", "entries": [
    {"startTime": 300.5, "value": 0.2, "hadRecentInput": True},
    {"startTime": 900.25, "value": 0.05, "hadRecentInput": True},
]})
with open("shifts.json", "w") as f:
    json.dump({"pages": pages}, f, indent=1)
