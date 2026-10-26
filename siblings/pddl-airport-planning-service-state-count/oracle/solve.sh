#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_service.py <<'PY'
import json
import re
from collections import deque
from pathlib import Path
p = Path('problem.pddl').read_text()
start = re.search(r'\(:init\s+\(at jet (\w+)\)', p).group(1)
exit_node = re.search(r'\(:goal\s+\(and\s+\(at jet (\w+)\)', p).group(1)
links = re.findall(r'\(connected (\w+) (\w+)\)', p)
required = set(re.findall(r'\(serviced (\w+)\)', p))
initial_service = set(re.findall(r'\(unserviced (\w+)\)', p))
origin = (start, frozenset())
dist = {origin: 0}
counts = {origin: 1}
queue = deque([origin])
while queue:
    state = queue.popleft()
    location, completed = state
    options = [(v, completed) for u, v in links if u == location]
    if location in initial_service and location not in completed:
        options.append((location, completed | {location}))
    for next_state in options:
        new_distance = dist[state] + 1
        if next_state not in dist:
            dist[next_state] = new_distance
            counts[next_state] = 0
            queue.append(next_state)
        if dist[next_state] == new_distance:
            counts[next_state] += counts[state]
goal_states = [s for s in dist if s[0] == exit_node and required.issubset(s[1])]
minimum = min(dist[s] for s in goal_states)
result = {'min_steps': minimum,
          'shortest_plans': sum(counts[s] for s in goal_states if dist[s] == minimum),
          'reachable_states': len(dist)}
Path('service_summary.json').write_text(json.dumps(result) + '\n')
PY
python /tmp/solve_service.py
