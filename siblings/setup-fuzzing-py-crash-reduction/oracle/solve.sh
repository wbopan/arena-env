#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_minimize.py <<'PY'
import itertools
import json
from pathlib import Path

root = Path('/root/work')
source = (root / 'crash.bin').read_bytes()
rule = json.loads((root / 'crash_rule.json').read_text())
magic = bytes.fromhex(rule['magic_hex'])
answer = None
for length in range(4, len(source) + 1):
    matches = []
    for positions in itertools.combinations(range(len(source)), length):
        data = bytes(source[i] for i in positions)
        if data.startswith(magic) and 0 in data[2:] and sum(data) % 11 == rule['remainder']:
            matches.append((data, positions))
    if matches:
        answer = min(matches)
        break
assert answer is not None
payload, positions = answer
(root / 'minimized.json').write_text(json.dumps({'minimized_hex': payload.hex(), 'length': len(payload), 'retained_indices': list(positions)}) + '\n', encoding='utf-8')
PY
python3 /tmp/solve_minimize.py
