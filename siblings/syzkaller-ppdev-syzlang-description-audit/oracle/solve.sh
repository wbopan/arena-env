#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve_audit.py <<'PY'
import csv
import json
import re
from pathlib import Path

root = Path('/root/work')
with (root / 'uapi_commands.csv').open(newline='') as f:
    directions = {r['name']: r['direction'] for r in csv.DictReader(f)}
text = (root / 'dev_audit.txt').read_text()
found = dict(re.findall(r'^ioctl\$([A-Z0-9_]+)\(fd fd_ppdev, cmd const\[\1\], arg ptr\[(in|out|inout), int32\]\)$', text, re.M))
constants = set()
for line in (root / 'dev_audit.txt.const').read_text().splitlines():
    match = re.fullmatch(r'\s*([A-Z][A-Z0-9_]*)\s*=\s*\d+\s*', line)
    if match:
        constants.add(match.group(1))
result = {
    'missing_constants': sorted(found.keys() - constants),
    'unused_constants': sorted(constants - found.keys()),
    'direction_mismatches': [
        {'name': name, 'expected': directions[name], 'actual': found[name]}
        for name in sorted(found) if found[name] != directions[name]
    ],
}
(root / 'audit.json').write_text(json.dumps(result, indent=2) + '\n')
PY
python3 /root/work/solve_audit.py
