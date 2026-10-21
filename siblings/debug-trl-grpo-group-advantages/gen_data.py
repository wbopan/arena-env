import csv
import random

random.seed(20240611)
rows = []
constant = {3: (0.0, 0.5), 11: (0.0, 0.0), 22: (1.0, 1.0)}
for p in range(30):
    pid = f"p{p:03d}"
    for c in range(8):
        if p in constant:
            corr, fmt = constant[p]
        else:
            prob = 0.15 + 0.7 * random.random()
            corr = 1.0 if random.random() < prob else 0.0
            fmt = round(random.random(), 3)
        rows.append([pid, c, corr, fmt])
random.shuffle(rows)
with open("rewards.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["prompt_id", "completion_id", "correctness", "format"])
    for r in rows:
        w.writerow(r)
