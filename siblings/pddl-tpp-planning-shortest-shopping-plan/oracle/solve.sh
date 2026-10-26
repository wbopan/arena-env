#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_shortest.py <<'PY'
import json
import re
from collections import deque
from pathlib import Path

text = Path('problem.pddl').read_text().lower()
initial, goal = text.split('(:init', 1)[1].split('(:goal', 1)
roads = sorted(set(re.findall(r'\(road (\w+) (\w+)\)', initial)))
offers = sorted(set(re.findall(r'\(available (\w+) (\w+)\)', initial)))
goals = frozenset(re.findall(r'\(owned (\w+)\)', goal))
start = ('depot', frozenset())
queue = deque([start])
parent = {start: None}
while queue:
    here, owned = state = queue.popleft()
    if goals <= owned:
        break
    choices = [((b, owned), f'drive(truck, {a}, {b})')
               for a, b in roads if a == here]
    choices += [((here, owned | {g}), f'buy(truck, {g}, {m})')
                for g, m in offers if m == here and g not in owned]
    for next_state, action in choices:
        if next_state not in parent:
            parent[next_state] = (state, action)
            queue.append(next_state)
else:
    raise ValueError('Unreachable goal')
actions = []
while parent[state] is not None:
    state, action = parent[state]
    actions.append(action)
actions.reverse()
Path('shortest_plan.json').write_text(json.dumps({
    'minimum_steps': len(actions), 'actions': actions
}, indent=2) + '\n')
PY
python /tmp/solve_shortest.py
