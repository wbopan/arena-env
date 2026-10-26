#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_parking.py <<'PY'
import re
from collections import deque
from pathlib import Path
p = Path('problem.pddl').read_text()
planes = ('jet1', 'jet2')
start = tuple(re.search(r'\(at ' + plane + r' (\w+)\)', p).group(1) for plane in planes)
targets = tuple(re.search(r'\(target ' + plane + r' (\w+)\)', p).group(1) for plane in planes)
edges = set(re.findall(r'\(edge (\w+) (\w+)\)', p))
queue = deque([start])
parent = {start: None}
finish = (None, None)
while queue:
    state = queue.popleft()
    if state == finish:
        break
    occupied = set(state) - {None}
    choices = []
    for i, node in enumerate(state):
        if node is None:
            continue
        if node == targets[i]:
            choices.append((f'park({planes[i]}, {node})', i, None))
        for a, b in edges:
            if a == node and b not in occupied:
                choices.append((f'move({planes[i]}, {a}, {b})', i, b))
    for action, i, destination in sorted(choices):
        successor = list(state)
        successor[i] = destination
        successor = tuple(successor)
        if successor not in parent:
            parent[successor] = (state, action)
            queue.append(successor)
if finish not in parent:
    raise RuntimeError('No parking plan')
plan = []
state = finish
while state != start:
    previous, action = parent[state]
    plan.append(action)
    state = previous
Path('parking.plan').write_text('\n'.join(reversed(plan)) + '\n')
PY
python /tmp/solve_parking.py
