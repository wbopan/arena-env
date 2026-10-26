#!/bin/bash
set -e
cat > /tmp/solve_coverage_frontier.py <<'PY'
import csv
import json
import math
from collections import defaultdict
from itertools import product
from pathlib import Path

root = Path('/root/work')
groups = defaultdict(list)
with (root / 'citsci.csv').open(newline='') as f:
    for r in csv.DictReader(f):
        groups[r['file_rad']].append((float(r['x']), float(r['y'])))
total = sum(len(p) for p in groups.values())

def evaluate(eps, minimum, weight):
    n_assigned, total_spread = 0, 0.0
    for points in groups.values():
        adjacency = [[j for j, b in enumerate(points) if math.hypot(weight*(a[0]-b[0]), (2-weight)*(a[1]-b[1])) <= eps] for a in points]
        core = {i for i, adjacent in enumerate(adjacency) if len(adjacent) >= minimum}
        labels = [-1] * len(points)
        cluster_count = 0
        for seed in range(len(points)):
            if seed not in core or labels[seed] != -1:
                continue
            queue = [seed]
            labels[seed] = cluster_count
            for i in queue:
                for j in adjacency[i]:
                    if labels[j] == -1:
                        labels[j] = cluster_count
                        if j in core:
                            queue.append(j)
            cluster_count += 1
        for cid in range(cluster_count):
            members = [p for i, p in enumerate(points) if labels[i] == cid]
            n_assigned += len(members)
            cx = sum(x for x, y in members)/len(members)
            cy = sum(y for x, y in members)/len(members)
            total_spread += sum(math.hypot(x-cx, y-cy) for x, y in members)
    return n_assigned/total, total_spread/n_assigned if n_assigned else float('inf')

candidates = []
for eps, minimum, weight in product((2, 3, 4), (2, 3), (0.7, 1.0, 1.3)):
    coverage, spread = evaluate(eps, minimum, weight)
    if coverage >= 0.4:
        candidates.append((eps, minimum, weight, coverage, spread))
front = []
for p in candidates:
    if any(q[3] >= p[3] and q[4] <= p[4] and (q[3] > p[3] or q[4] < p[4]) for q in candidates):
        continue
    front.append({'epsilon': p[0], 'min_samples': p[1], 'shape_weight': round(p[2], 5), 'coverage': round(p[3], 5), 'spread_px': round(p[4], 5)})
(root / 'frontier.json').write_text(json.dumps(front, indent=2) + '\n')
PY
python3 /tmp/solve_coverage_frontier.py
