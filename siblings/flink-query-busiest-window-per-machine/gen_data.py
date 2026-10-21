import gzip
import random
import os

random.seed(9090)
os.makedirs('data', exist_ok=True)
S = 1_000_000
W = 300 * S
machines = [str(400000 + k * 331 + random.randint(0, 50)) for k in range(12)]
jobs = [6300000000 + i * 577 for i in range(18)]
rows = []


def row(t, jid, idx, m, et):
    return '%d,,%d,%d,%s,%d,u%d,%d,%d,0.0625,0.0311,0.0001,0' % (
        t, jid, idx, m, et, jid % 5, jid % 4, random.randint(0, 11))


for mi, m in enumerate(machines):
    for _ in range(random.randint(15, 35)):
        rows.append(row(random.randint(600 * S, 7800 * S), random.choice(jobs), random.randint(0, 200), m, 1))
    w = random.randint(3, 25)
    sub = random.sample(jobs, 4)
    for _ in range(random.randint(6, 14)):
        rows.append(row(w * W + random.randint(0, W - 1), random.choice(sub), random.randint(0, 200), m, 1))
    for _ in range(10):
        rows.append(row(random.randint(600 * S, 7800 * S), random.choice(jobs), random.randint(0, 200), m, random.choice([2, 3, 4, 5])))
    if mi % 3 == 0:
        for _ in range(random.randint(12, 20)):
            rows.append(row(0, random.choice(jobs), random.randint(0, 200), m, 1))
    if mi % 4 == 1:
        k = random.randint(3, 25)
        for _ in range(random.randint(2, 5)):
            rows.append(row(k * W, random.choice(jobs), random.randint(0, 200), m, 1))
for _ in range(100):
    rows.append(row(random.randint(0, 7800 * S), random.choice(jobs), random.randint(0, 200), '', 0))

random.shuffle(rows)
with open('data/task_events.csv.gz', 'wb') as f:
    f.write(gzip.compress(('\n'.join(rows) + '\n').encode(), mtime=0))
