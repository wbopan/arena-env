import json
import random

random.seed(20240611)
nodes = list(range(65001, 65041))
random.shuffle(nodes)
pref = {}
idx = 0
for L in (2, 3, 4):
    cyc = nodes[idx:idx + L]
    idx += L
    for i, a in enumerate(cyc):
        pref[a] = cyc[(i + 1) % L]
for a in nodes[idx:idx + 5]:
    pref[a] = None
idx += 5
assigned = list(nodes[:idx])
for a in nodes[idx:]:
    if random.random() < 0.15:
        pref[a] = random.randint(64512, 64520)
    else:
        pref[a] = random.choice(assigned)
    assigned.append(a)
out = {str(k): pref[k] for k in sorted(pref)}
with open('preferences.json', 'w') as f:
    json.dump(out, f, indent=2)
