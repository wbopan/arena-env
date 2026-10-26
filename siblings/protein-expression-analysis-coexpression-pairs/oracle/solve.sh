#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_coexpression.py <<'PY'
import json
from math import sqrt
from openpyxl import load_workbook

wb = load_workbook('coexpression_panel.xlsx', data_only=True)
rows = list(wb['Data'].values)
profiles = {row[0]: row[1:] for row in rows[1:]}
ranked = []
for pair_id, a, b in list(wb['Pairs'].values)[1:]:
    x, y = profiles[a], profiles[b]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    dx = [v - mx for v in x]
    dy = [v - my for v in y]
    correlation = sum(u * v for u, v in zip(dx, dy)) / sqrt(sum(u * u for u in dx) * sum(v * v for v in dy))
    ranked.append((pair_id, a, b, correlation))
ranked.sort(key=lambda item: (-abs(item[3]), item[0]))
output = {'pairs': [{'pair_id': i, 'protein_a': a, 'protein_b': b, 'pearson_r': round(r, 4)} for i, a, b, r in ranked], 'strongest_pair_id': ranked[0][0]}
with open('coexpression_pairs.json', 'w') as f:
    json.dump(output, f, indent=2)
PY
python /tmp/solve_coexpression.py
