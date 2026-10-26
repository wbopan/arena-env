#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_exam_frontier.py <<'PY'
import csv
import itertools
import json
from collections import Counter

with open('instance.json') as f:
    spec = json.load(f)
def table(path, columns):
    with open(path, newline='') as f:
        return {tuple(row[k] for k in columns): int(row['count']) for row in csv.DictReader(f)}
pairs = table('pair_counts.csv', ('first', 'second'))
triples = table('triple_counts.csv', ('first', 'second', 'third'))
frequency = Counter()
for sequence in itertools.permutations(spec['blocks']):
    if any(spec['slot_order'][sequence.index(block)] not in spec['early_slots'] for block in spec['large_blocks']):
        continue
    first = sum(pairs[sequence[i:i + 2]] for i in range(6))
    second = sum(triples[sequence[i:i + 3]] for i in range(5))
    frequency[first, second] += 1
frontier = []
lowest_triple = float('inf')
for (first, second), count in sorted(frequency.items()):
    if second < lowest_triple:
        frontier.append({'pair_cost': first, 'triple_cost': second, 'multiplicity': count})
        lowest_triple = second
with open('frontier.json', 'w') as f:
    json.dump({'frontier': frontier}, f, indent=2)
PY
python /tmp/solve_exam_frontier.py
