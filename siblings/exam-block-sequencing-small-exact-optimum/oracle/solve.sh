#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_opt.py <<'EOF'
import csv, json, itertools
inst = json.load(open('instance.json'))
pair = {(r['block_i'], r['block_j']): int(r['count']) for r in csv.DictReader(open('pair_counts.csv'))}
trip = {(r['block_i'], r['block_j'], r['block_k']): int(r['count']) for r in csv.DictReader(open('triplet_counts.csv'))}
order = inst['slot_order']
pos = {s: i for i, s in enumerate(order)}
bi = [pos[s] for s in inst['b2b_start']]
ti = [pos[s] for s in inst['triple_start']]
early = {pos[s] for s in inst['early_slots']}
large = set(inst['large_blocks'])
wb, wt = inst['weights']['b2b'], inst['weights']['triple']
best, bestp = None, None
for p in itertools.permutations(inst['blocks']):
    if any(p[i] in large and i not in early for i in range(len(p))):
        continue
    v = wb * sum(pair.get((p[i], p[i + 1]), 0) for i in bi) + wt * sum(trip.get((p[i], p[i + 1], p[i + 2]), 0) for i in ti)
    if best is None or v < best:
        best, bestp = v, p
with open('schedule.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['slot', 'block'])
    for s, b in zip(order, bestp):
        w.writerow([s, b])
print('objective', best)
EOF
python3 /tmp/solve_opt.py
