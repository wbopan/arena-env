import csv
import json
import random

random.seed(20240611)

days = ['Mon', 'Tue', 'Wed', 'Thu']
periods = ['AM', 'PM', 'EV']
slots = [f'{d}-{p}' for d in days for p in periods]
blocks = [f'B{i:02d}' for i in range(1, 13)]
n = len(slots)
idx = {s: i for i, s in enumerate(slots)}

inst = {
    'slot_order': slots,
    'blocks': blocks,
    'eve_morn_start': [s for s in slots if s.endswith('EV') and idx[s] + 1 < n],
    'other_b2b_start': [s for s in slots if not s.endswith('EV')],
    'triple_day_start': [s for s in slots if s.endswith('AM')],
    'triple_24_start': [s for s in slots if (s.endswith('PM') or s.endswith('EV')) and idx[s] + 2 < n],
    'four_start': [s for s in slots if idx[s] + 3 < n],
}
with open('instance.json', 'w') as f:
    json.dump(inst, f, indent=2)

with open('pair_counts.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['block_i', 'block_j', 'count'])
    for a in blocks:
        for b in blocks:
            if a != b and random.random() < 0.7:
                w.writerow([a, b, random.randint(1, 15)])

with open('triplet_counts.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['block_i', 'block_j', 'block_k', 'count'])
    for a in blocks:
        for b in blocks:
            for c in blocks:
                if len({a, b, c}) == 3 and random.random() < 0.3:
                    w.writerow([a, b, c, random.randint(1, 6)])

perm = blocks[:]
random.shuffle(perm)
rows = list(zip(slots, perm))
random.shuffle(rows)
with open('schedule.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['slot', 'block'])
    for r in rows:
        w.writerow(r)
