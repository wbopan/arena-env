#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_box_induction.py <<'PY'
import json
from pathlib import Path

root = Path('/root/work')
answers = []
for p in json.loads((root / 'recurrences.json').read_text()):
    x0, x1, y0, y1 = p['box']
    def contained(point):
        x, y = point
        return x0 <= x <= x1 and y0 <= y <= y1
    corners = sorted((x, y) for x in {x0, x1} for y in {y0, y1})
    witness = None
    for x, y in corners:
        image = (p['a'] * x + p['b'] * y + p['c'],
                 p['d'] * x + p['e'] * y + p['f'])
        if not contained(image):
            witness = [x, y]
            break
    base = contained(p['start'])
    step = witness is None
    answers.append(dict(id=p['id'], base_ok=base, step_ok=step,
                        induction_ready=base and step, witness=witness))
(root / 'obligations.json').write_text(json.dumps(answers, indent=2) + '\n')
PY
python3 /tmp/solve_box_induction.py
