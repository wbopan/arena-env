#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_trace.py <<'PY'
import csv
import re
from pathlib import Path
p = Path('problem.pddl').read_text()
loc = re.search(r'\(:init\s+\(at\s+jet\s+(\w+)\)', p).group(1)
edges = set(re.findall(r'\(connected\s+(\w+)\s+(\w+)\)', p))
with open('trace.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['step', 'action', 'valid', 'location'])
    writer.writerow([0, 'INIT', 'true', loc])
    for index, line in enumerate(Path('candidate.plan').read_text().splitlines(), 1):
        origin, destination = re.fullmatch(r'move\(jet,\s*(\w+),\s*(\w+)\)', line).groups()
        ok = origin == loc and (origin, destination) in edges
        if ok:
            loc = destination
        writer.writerow([index, line, str(ok).lower(), loc])
        if not ok:
            break
PY
python /tmp/solve_trace.py
