#!/bin/bash
set -e
cat > /root/work/solve_pca.py <<'PY'
import csv
import json
import numpy as np
from pathlib import Path
root = Path('/root/work')
names = ['AirTemp', 'Radiation', 'WindSpeed', 'Inflow', 'Runoff', 'DevelopedPct', 'AgriculturePct', 'TreeCoverPct']
groups = {'Heat': names[:2], 'Flow': names[3:5], 'Wind': names[2:3], 'Human': names[5:]}
data = {}
for filename in ('climate.csv', 'hydrology.csv', 'land_cover.csv'):
    with (root / filename).open(newline='') as f:
        for row in csv.DictReader(f):
            data.setdefault(int(row['Year']), {}).update(row)
x = np.array([[float(data[year][name]) for name in names] for year in sorted(data)])
z = (x - x.mean(axis=0)) / x.std(axis=0, ddof=0)
values, vectors = np.linalg.eigh(z.T @ z / len(z))
order = np.argsort(values)[::-1]
values = values[order]
pc1 = vectors[:, order[0]]
if pc1[np.argmax(abs(pc1))] < 0:
    pc1 = -pc1
shares = {group: 100 * sum(pc1[names.index(name)] ** 2 for name in members) for group, members in groups.items()}
winner = max(shares, key=shares.get)
result = {'pc1_variance_pct': round(100 * values[0] / values.sum(), 6), 'pc2_variance_pct': round(100 * values[1] / values.sum(), 6), 'pc1_loadings': {name: round(float(pc1[i]), 6) for i, name in enumerate(names)}, 'dominant_category': winner, 'category_share_pct': round(float(shares[winner]), 6)}
(root / 'pca_summary.json').write_text(json.dumps(result, indent=2) + '\n')
PY
python /root/work/solve_pca.py
