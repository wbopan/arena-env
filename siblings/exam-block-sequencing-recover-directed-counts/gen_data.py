import csv
import itertools
import json
import random

import numpy as np

random.seed(8027)
blocks = [f'B{i}' for i in range(6)]
slots = ['D1A', 'D1C', 'D2A', 'D3B', 'D4A', 'D4C']
missing = [('B0', 'B2'), ('B3', 'B1'), ('B4', 'B5'), ('B2', 'B4')]
values = {p: random.randint(1, 6) for p in itertools.permutations(blocks, 2)}
with open('instance.json', 'w') as f:
    json.dump({'slot_order': slots, 'blocks': blocks}, f)
with open('missing_pairs.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['first', 'second'])
    w.writerows(missing)
with open('pair_counts.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['first', 'second', 'count'])
    for p in itertools.permutations(blocks, 2):
        if p not in missing:
            w.writerow([*p, values[p]])
perms = list(itertools.permutations(blocks))
random.shuffle(perms)
chosen = []
rank = 0
for p in perms:
    edges = list(zip(p, p[1:]))
    vector = [edges.count(key) for key in missing]
    candidate = np.array([v for _, v in chosen] + [vector], dtype=float)
    new_rank = np.linalg.matrix_rank(candidate)
    if new_rank > rank:
        chosen.append((p, vector))
        rank = new_rank
    if rank == 4:
        break
assert rank == 4
chosen.extend((p, None) for p in perms if p not in {q for q, _ in chosen})
with open('observations.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow([*slots, 'total'])
    for p, _ in chosen[:12]:
        w.writerow([*p, sum(values[a, b] for a, b in zip(p, p[1:]))])
