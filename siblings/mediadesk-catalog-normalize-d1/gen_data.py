import csv, json, random
random.seed(20261551)
LEVEL = 1
WORDS = ["harbour", "night", "signal", "orchard", "glass", "river", "atlas", "ember", "quiet", "north", "copper", "tide"]
def fmt(sec):
    h, m, s = sec // 3600, sec // 60 % 60, sec % 60
    k = random.randrange(4)
    if k == 0:
        return "%d:%02d:%02d" % (h, m, s)
    if k == 1 and h == 0:
        return "%d:%02d" % (m, s)
    if k == 2:
        return "%ds" % sec
    return (("%dh" % h) if h else "") + (("%dm" % m) if m else "") + (("%ds" % s) if s or not (h or m) else "")
rows = []
n = random.randint(9, 14)
for i in range(n):
    aid = "MA-%04d" % random.randint(100, 9999)
    title = " ".join(random.sample(WORDS, random.randint(1, 3))).title()
    if random.random() < 0.4:
        title = "  " + title.replace(" ", "   ") + " "
    sec = random.randint(25, 5400) if random.random() < 0.8 else random.choice([60, 3600, 600])
    rows.append([aid if random.random() < 0.7 else aid.lower(), title, fmt(sec), "2026-%02d-%02dT%02d:00:00Z" % (random.randint(1, 9), random.randint(1, 28), random.randint(0, 23))])
if LEVEL >= 2:
    for _ in range(random.randint(2, 4)):
        r = list(random.choice(rows))
        r[0] = r[0].upper() if random.random() < 0.5 else r[0].lower()
        r[2] = fmt(random.randint(25, 5400))
        r[3] = "2026-%02d-%02dT%02d:00:00Z" % (random.randint(1, 9), random.randint(1, 28), random.randint(0, 23))
        rows.append(r)
random.shuffle(rows)
with open("library.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["asset_id", "title", "duration", "updated_at"]); w.writerows(rows)
job = {}
if LEVEL >= 2:
    job["playlist_cap_sec"] = random.randint(1800, 7200)
json.dump(job, open("job.json", "w"))
