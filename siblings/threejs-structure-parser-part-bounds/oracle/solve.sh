#!/bin/bash
set -euo pipefail
cat > /tmp/solve_bounds.py <<'PY'
import csv
import json
from pathlib import Path

scene = json.loads(Path('/root/work/scene.json').read_text())['object']
parts = {}
def apply(m, v):
    x, y, z = v
    return [m[0]*x + m[4]*y + m[8]*z + m[12],
            m[1]*x + m[5]*y + m[9]*z + m[13],
            m[2]*x + m[6]*y + m[10]*z + m[14]]
def visit(node, matrices, part):
    matrices = matrices + [node['matrix']]
    if node['type'] == 'Group' and node.get('name'):
        part = node['name']
        parts[part] = [0, []]
    if node['type'] == 'Mesh' and part is not None:
        parts[part][0] += 1
        raw = node['positions']
        for i in range(0, len(raw), 3):
            vertex = raw[i:i+3]
            for matrix in matrices[::-1]:
                vertex = apply(matrix, vertex)
            parts[part][1].append(vertex)
    for child in node.get('children', []):
        visit(child, matrices, part)
visit(scene, [], None)
header = ['part', 'mesh_count', 'vertex_count', 'min_x', 'min_y', 'min_z', 'max_x', 'max_y', 'max_z', 'centroid_x', 'centroid_y', 'centroid_z']
with Path('/root/work/part_bounds.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for name in sorted(parts):
        count, points = parts[name]
        if not points:
            continue
        columns = list(zip(*points))
        values = [min(c) for c in columns] + [max(c) for c in columns] + [sum(c)/len(c) for c in columns]
        writer.writerow([name, count, len(points)] + [f'{v:.6f}' for v in values])
PY
python /tmp/solve_bounds.py
