import json
import random

random.seed(20240611)
BS = 64
CAP = 40
_nid = [5000]


def new_block():
    _nid[0] += random.randint(1, 9)
    return _nid[0]


systems = [[new_block() for _ in range(random.randint(2, 4))] for _ in range(4)]
sessions = []
for _ in range(18):
    sessions.append({"hist": list(random.choice(systems)), "turns": random.randint(2, 6)})

pool = [i for i, s in enumerate(sessions) for _ in range(s["turns"])]
random.shuffle(pool)

reqs = []
used_ids = set()
t = 0
for i in pool:
    s = sessions[i]
    if random.random() < 0.12 and len(s["hist"]) > 2:
        k = random.randint(1, len(s["hist"]) - 1)
        ids = s["hist"][:k] + [new_block() for _ in range(random.randint(1, 2))]
    else:
        if len(s["hist"]) < 14:
            s["hist"].extend(new_block() for _ in range(random.randint(1, 2)))
        ids = list(s["hist"])
    L = (len(ids) - 1) * BS + random.randint(1, BS)
    t += random.choice([0, 0, 1, 3, 5, 8, 13, 21])
    while True:
        rid = "%06x" % random.randint(0, 0xFFFFFF)
        if rid not in used_ids:
            used_ids.add(rid)
            break
    reqs.append({"request_id": rid, "timestamp": t, "input_length": L,
                 "output_length": random.randint(8, 400), "hash_ids": ids})

random.shuffle(reqs)
with open("trace.jsonl", "w") as f:
    for r in reqs:
        f.write(json.dumps(r) + "\n")
with open("config.json", "w") as f:
    json.dump({"block_size": BS, "cache_capacity_blocks": CAP, "policy": "LRU"}, f, indent=2)
