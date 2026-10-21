import json
import random

random.seed(777)
BS = 32
_nid = [100]


def new_block():
    _nid[0] += random.randint(1, 6)
    return _nid[0]


systems = [[new_block() for _ in range(random.randint(3, 5))] for _ in range(5)]
weights = [0.45, 0.25, 0.15, 0.1, 0.05]
sessions = []
for _ in range(20):
    base = random.choices(systems, weights=weights)[0]
    sessions.append({"hist": list(base), "turns": random.randint(2, 5)})

pool = [i for i, s in enumerate(sessions) for _ in range(s["turns"])]
random.shuffle(pool)
n_scan = 14
slots = pool + [-1] * n_scan
random.shuffle(slots)

t = 1000
reqs = []
for i in slots:
    if i == -1:
        ids = [new_block() for _ in range(random.randint(2, 6))]
    else:
        s = sessions[i]
        if len(s["hist"]) < 12:
            s["hist"].extend(new_block() for _ in range(random.randint(1, 2)))
        ids = list(s["hist"])
    L = (len(ids) - 1) * BS + random.randint(1, BS)
    t += random.randint(1, 30)
    reqs.append({"timestamp": t, "input_length": L,
                 "output_length": random.randint(16, 300), "hash_ids": ids})

with open("trace.jsonl", "w") as f:
    for r in reqs:
        f.write(json.dumps(r) + "\n")
with open("config.json", "w") as f:
    json.dump({"block_size": BS, "policies": ["FIFO", "LRU", "LFU"],
               "capacities": [16, 32, 64]}, f, indent=2)
