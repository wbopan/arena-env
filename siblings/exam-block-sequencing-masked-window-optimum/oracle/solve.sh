#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_exam_masked.py <<'PY'
import csv
import itertools
import json

with open('instance.json') as f:
    d = json.load(f)
with open('pair_counts.csv', newline='') as f:
    pairs = {(r['first'], r['second']): int(r['count']) for r in csv.DictReader(f)}
with open('triple_counts.csv', newline='') as f:
    triples = {(r['first'], r['second'], r['third']): int(r['count']) for r in csv.DictReader(f)}
best = None
for p in itertools.permutations(d['blocks']):
    if any(d['slot_order'][p.index(b)] not in d['early_slots'] for b in d['large_blocks']):
        continue
    score = sum(pairs[p[i], p[i + 1]] for i in d['pair_starts'])
    score += 3 * sum(triples[p[i], p[i + 1], p[i + 2]] for i in d['triple_starts'])
    if best is None or (score, p) < best:
        best = (score, p)
with open('schedule.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['slot', 'block'])
    w.writerows(zip(d['slot_order'], best[1]))
PY
python /tmp/solve_exam_masked.py
