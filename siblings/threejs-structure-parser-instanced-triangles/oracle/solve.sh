#!/bin/bash
set -euo pipefail
cat > /tmp/solve_instances.py <<'PY'
import json
from pathlib import Path

data = json.loads(Path('/root/work/instances.json').read_text())
coords = data['geometry']['positions']
points = list(zip(coords[::3], coords[1::3], coords[2::3]))
indices = data['geometry']['indices']
def transform(m, p):
    x, y, z = p
    return (m[0]*x + m[4]*y + m[8]*z + m[12],
            m[1]*x + m[5]*y + m[9]*z + m[13],
            m[2]*x + m[6]*y + m[10]*z + m[14])
lines = []
for number, instance in enumerate(data['instance_matrices']):
    for point in points:
        world = transform(data['mesh_matrix'], transform(instance, point))
        lines.append('v ' + ' '.join(f'{value:.6f}' for value in world))
    offset = number * len(points) + 1
    for a, b, c in zip(indices[::3], indices[1::3], indices[2::3]):
        lines.append(f'f {offset+a} {offset+b} {offset+c}')
Path('/root/work/expanded.obj').write_text('\n'.join(lines) + '\n')
PY
python /tmp/solve_instances.py
