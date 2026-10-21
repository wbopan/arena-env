import csv
import json
import random

random.seed(7713)

slots = ['Mon-AM', 'Mon-PM', 'Mon-EV', 'Tue-AM', 'Tue-PM', 'Tue-EV', 'Wed-AM', 'Wed-PM']
blocks = [f'B{i:02d}' for i in range(1, 9)]
large = sorted(random.sample(blocks, 2))
inst = {
    'slot_order': slots,
    'blocks': blocks,
    'large_blocks': large,
    'early_slots': slots[:3],
    'b2b_start': slots[:7],
    'triple_start': ['Mon-AM', 'Mon-PM', 'Tue-AM', 'Tue-PM', 'Tue-EV'],
    'weights': {'b2b': 1, 'triple': 10},
}
with open('instance.json', 'w') as f:
    json.dump(inst, f, indent=2)

with open('pair_counts.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['block_i', 'block_j', 'count'])
    for a in blocks:
        for b in blocks:
            if a != b and random.random() < 0.8:
                w.writerow([a, b, random.randint(1, 20)])

with open('triplet_counts.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['block_i', 'block_j', 'block_k', 'count'])
    for a in blocks:
        for b in blocks:
            for c in blocks:
                if len({a, b, c}) == 3 and random.random() < 0.35:
                    w.writerow([a, b, c, random.randint(1, 8)])
