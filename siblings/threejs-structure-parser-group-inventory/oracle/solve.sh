#!/bin/bash
set -euo pipefail
cat > /tmp/solve_inventory.py <<'PY'
import json
from pathlib import Path

root = json.loads(Path('/root/work/scene.json').read_text())['object']
parts = {}
loose = []
def walk(node, parent):
    kind = node.get('type')
    if kind == 'Group' and node.get('name'):
        label = node['name']
        parts[label] = {'name': label, 'parent': parent, 'meshes': []}
        parent = label
    if kind == 'Mesh':
        target = loose if parent is None else parts[parent]['meshes']
        target.append(node['name'])
    for child in node.get('children', []):
        walk(child, parent)
walk(root, None)
for part in parts.values():
    part['meshes'].sort()
answer = {'groups': [parts[k] for k in sorted(parts)], 'unowned_meshes': sorted(loose)}
Path('/root/work/group_inventory.json').write_text(json.dumps(answer, indent=2) + '\n')
PY
python /tmp/solve_inventory.py
