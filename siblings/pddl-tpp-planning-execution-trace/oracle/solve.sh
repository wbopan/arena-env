#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_trace.py <<'PY'
import csv
import re
from pathlib import Path

text = Path('problem.pddl').read_text().lower()
initial, goal = text.split('(:init', 1)[1].split('(:goal', 1)
roads = set(re.findall(r'\(road (\w+) (\w+)\)', initial))
stock = set(re.findall(r'\(stock (\w+) (\w+)\)', initial))
goals = set(re.findall(r'\(delivered (\w+)\)', goal))
location = 'depot'
cargo = None
purchased = set()
delivered = set()
fields = ['step', 'action', 'applicable', 'location', 'cargo', 'delivered', 'goal_after']
with Path('execution_trace.csv').open('w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(fields)
    for step, line in enumerate(Path('candidate.plan').read_text().splitlines(), 1):
        match = re.fullmatch(r'(\w+)\(truck, (\w+)(?:, (\w+))?\)', line)
        if match is None:
            raise ValueError(line)
        action, x, y = match.groups()
        if action == 'drive':
            applicable = y is not None and x == location and (x, y) in roads
            if applicable:
                location = y
        elif action == 'buy':
            applicable = y is not None and y == location and (x, y) in stock
            if applicable:
                purchased.add((x, y))
        elif action == 'load':
            applicable = y is not None and y == location and cargo is None and (x, y) in purchased
            if applicable:
                cargo = x
        elif action == 'unload':
            applicable = y is None and location == 'depot' and cargo == x
            if applicable:
                delivered.add(x)
                cargo = None
        else:
            raise ValueError(action)
        writer.writerow([step, line, int(applicable), location, cargo or '-',
                         ';'.join(sorted(delivered)) or '-', int(goals <= delivered)])
PY
python /tmp/solve_trace.py
