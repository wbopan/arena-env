import json
import random

random.seed(4242)
keys = ["user%04d" % k for k in random.sample(range(10000), 15)]
versions = {}
events = []
tid = 1
for k in keys:
    n = random.randint(4, 8)
    w = 0
    a = random.randint(1, 10)
    vs = []
    for _ in range(n):
        w += random.randint(3, 25)
        a += random.randint(3, 9)
        vs.append((w, a))
        events.append({"ev": "write", "txn": tid, "key": k, "wts": w, "ats": a})
        tid += 1
    versions[k] = vs

atid = 5001
for t in range(70):
    k = random.choice(keys)
    vs = versions[k]
    i = random.randint(-1, len(vs) - 2)
    j = random.randint(i + 1, len(vs) - 1)
    lw = 0 if i < 0 else vs[i][0]
    succ = vs[i + 1][0]
    cw = vs[j][0]
    ats = vs[j][1] + random.randint(1, 2)
    r = random.random()
    if r < 0.1:
        c = succ
    elif r < 0.55:
        c = random.randint(lw + 1, succ - 1)
    else:
        c = succ + random.randint(1, 40)
    events.append({"ev": "abort", "txn": atid, "key": k, "local_wts": lw,
                   "current_wts": cw, "commit_ts": c, "ats": ats})
    atid += random.randint(1, 5)

random.shuffle(events)
with open("trace.jsonl", "w") as f:
    for e in events:
        f.write(json.dumps(e, separators=(",", ":")) + "\n")
