#!/usr/bin/env bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_delivery.py <<'PY'
import re
from collections import deque
from pathlib import Path

text = Path('problem.pddl').read_text().lower()
init, goal = text.split('(:init', 1)[1].split('(:goal', 1)
roads = set(re.findall(r'\(road (\w+) (\w+)\)', init))
stock = set(re.findall(r'\(stock (\w+) (\w+)\)', init))
goods = sorted(set(re.findall(r'\(delivered (\w+)\)', goal)))

def route(start, end):
    queue = deque([(start, [])])
    seen = {start}
    while queue:
        here, path = queue.popleft()
        if here == end:
            return path
        for a, b in sorted(roads):
            if a == here and b not in seen:
                seen.add(b)
                queue.append((b, path + [(a, b)]))
    raise ValueError('No route')

lines = []
for good in goods:
    market = sorted(m for g, m in stock if g == good)[0]
    for a, b in route('depot', market):
        lines.append(f'drive(truck, {a}, {b})')
    lines += [f'buy(truck, {good}, {market})', f'load(truck, {good}, {market})']
    for a, b in route(market, 'depot'):
        lines.append(f'drive(truck, {a}, {b})')
    lines.append(f'unload(truck, {good})')
Path('delivery.plan').write_text('\n'.join(lines) + '\n')
PY
python /tmp/solve_delivery.py
