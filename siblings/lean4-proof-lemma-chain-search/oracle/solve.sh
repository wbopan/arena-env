#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_lemma_chains.py <<'PY'
import csv
import heapq
from pathlib import Path

root = Path('/root/work')
def load(name):
    with (root / name).open(newline='') as stream:
        return list(csv.DictReader(stream))

adj = {}
for edge in load('lemmas.csv'):
    adj.setdefault(edge['premise'], set()).add(edge['conclusion'])

with (root / 'chains.csv').open('w', newline='') as stream:
    out = csv.writer(stream)
    out.writerow(['goal_id', 'status', 'chain'])
    for goal in load('goals.csv'):
        source, target = goal['known'], goal['target']
        heap = [(0, (source,))]
        visited = set()
        answer = None
        while heap:
            length, path = heapq.heappop(heap)
            node = path[-1]
            if node in visited:
                continue
            visited.add(node)
            if node == target:
                answer = path
                break
            for nxt in adj.get(node, ()):
                if nxt not in visited:
                    heapq.heappush(heap, (length + 1, path + (nxt,)))
        out.writerow([goal['goal_id'], 'proved' if answer else 'missing',
                      '>'.join(answer) if answer else ''])
PY
python3 /tmp/solve_lemma_chains.py
