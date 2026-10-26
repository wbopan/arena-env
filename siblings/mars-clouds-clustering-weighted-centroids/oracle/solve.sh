#!/bin/bash
set -e
cat > /tmp/solve_weighted_centroids.py <<'PY'
import csv
import math
from collections import defaultdict
from pathlib import Path

root = Path('/root/work')
images = defaultdict(list)
with (root / 'citsci.csv').open(newline='') as f:
    for row in csv.DictReader(f):
        images[row['file_rad']].append((float(row['x']), float(row['y'])))

out = []
for name, points in sorted(images.items()):
    adj = [[j for j, b in enumerate(points) if math.hypot(1.5*(a[0]-b[0]), 0.5*(a[1]-b[1])) <= 2.5] for a in points]
    core = {i for i, near in enumerate(adj) if len(near) >= 3}
    labels = [-1] * len(points)
    count = 0
    for seed in range(len(points)):
        if seed not in core or labels[seed] >= 0:
            continue
        todo = [seed]
        labels[seed] = count
        for i in todo:
            for j in adj[i]:
                if labels[j] < 0:
                    labels[j] = count
                    if j in core:
                        todo.append(j)
        count += 1
    for cid in range(count):
        chosen = [p for i, p in enumerate(points) if labels[i] == cid]
        out.append((name, cid, len(chosen), f'{sum(p[0] for p in chosen)/len(chosen):.4f}', f'{sum(p[1] for p in chosen)/len(chosen):.4f}'))
with (root / 'centroids.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['file_rad', 'cluster_id', 'n_points', 'centroid_x', 'centroid_y'])
    writer.writerows(out)
PY
python3 /tmp/solve_weighted_centroids.py
