#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_exam_counts.py <<'PY'
import csv
import itertools
import json

with open('instance.json') as f:
    spec = json.load(f)
def load(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))
missing = [(r['first'], r['second']) for r in load('missing_pairs.csv')]
known = {(r['first'], r['second']): int(r['count']) for r in load('pair_counts.csv')}
conditions = []
for row in load('observations.csv'):
    schedule = [row[s] for s in spec['slot_order']]
    edges = list(zip(schedule, schedule[1:]))
    target = int(row['total']) - sum(known.get(edge, 0) for edge in edges)
    conditions.append(([sum(edge == key for edge in edges) for key in missing], target))
answers = [v for v in itertools.product(range(1, 7), repeat=len(missing)) if all(sum(a * b for a, b in zip(coef, v)) == target for coef, target in conditions)]
assert len(answers) == 1
with open('inferred_pairs.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['first', 'second', 'count'])
    w.writerows((*pair, value) for pair, value in zip(missing, answers[0]))
PY
python /tmp/solve_exam_counts.py
