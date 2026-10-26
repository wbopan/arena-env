#!/bin/bash
set -e
cat > /tmp/solve_greedy_pairs.py <<'PY'
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

root = Path('/root/work')
def read(filename, id_column):
    groups = defaultdict(list)
    with (root / filename).open(newline='') as f:
        for row in csv.DictReader(f):
            groups[row['file_rad']].append((int(row[id_column]), float(row['x']), float(row['y'])))
    return groups

clouds = read('centroids.csv', 'cluster_id')
experts = read('expert.csv', 'expert_id')
images = []
for image in sorted(clouds.keys() | experts.keys()):
    possible = []
    for cid, x, y in clouds[image]:
        for eid, u, v in experts[image]:
            distance = math.hypot(x-u, y-v)
            if distance <= 16:
                possible.append((distance, cid, eid))
    used_clusters, used_experts, accepted = set(), set(), []
    for distance, cid, eid in sorted(possible):
        if cid in used_clusters or eid in used_experts:
            continue
        used_clusters.add(cid)
        used_experts.add(eid)
        accepted.append({'cluster_id': cid, 'expert_id': eid, 'distance_px': round(distance, 3)})
    images.append({'file_rad': image, 'matches': accepted, 'unmatched_clusters': sorted(cid for cid, _, _ in clouds[image] if cid not in used_clusters), 'unmatched_experts': sorted(eid for eid, _, _ in experts[image] if eid not in used_experts)})
(root / 'matches.json').write_text(json.dumps({'images': images}, indent=2) + '\n')
PY
python3 /tmp/solve_greedy_pairs.py
