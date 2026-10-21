import json
import random
import statistics

random.seed(20240607)

N = 600
op = random.randint(45, 85)
e = [0.0] * N
for i in range(op):
    e[i] = random.uniform(18, 40)

i = 22
while i < op - 8:
    if random.random() < 0.3:
        L = random.choice([1, 2])
        for k in range(L):
            e[i + k] = random.uniform(130, 200)
        i += L + 2
    else:
        i += 1
e[op - 4] = random.uniform(130, 200)
e[op - 3] = random.uniform(130, 200)

for i in range(op, N):
    e[i] = random.uniform(300, 900)

segs = []
s0 = random.randint(3, 8)
segs.append([s0, s0 + random.randint(2, 4)])
segs.append([op - 6, op])

content = []
pos = op + 8
while True:
    pos += random.randint(15, 40)
    L = random.randint(2, 6)
    if pos + L > N - 20:
        break
    content.append([pos, pos + L])
    pos += L

a = content[1]
segs.append([a[0] + 1, a[1] + 2])
b = content[3]
segs.append([b[1], b[1] + 2])
segs.extend(content)
segs.append([N - 3, N + 4])

for s, t in segs:
    for k in range(max(s, op), min(t, N)):
        e[k] = random.uniform(10, 40)

random.shuffle(segs)
energies = [round(v, 1) for v in e]

with open("energies.json", "w") as f:
    json.dump({
        "sample_rate": 16000,
        "window_seconds": 1,
        "total_seconds": N,
        "energies": energies,
        "stats": {
            "min": min(energies),
            "max": max(energies),
            "mean": round(statistics.mean(energies), 2),
            "std": round(statistics.pstdev(energies), 2),
        },
    }, f)

with open("pauses.json", "w") as f:
    json.dump({"segments": [{"start": s, "end": t, "duration": t - s} for s, t in segs]}, f, indent=1)
