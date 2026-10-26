#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_template.py <<'PY'
import csv
from pathlib import Path
import numpy as np

root = Path('/root/work')
with np.load(root / 'templates.npz') as t:
    channels = str(t['channels']).split(',')
    patterns = [('P', t['p_template']), ('S', t['s_template'])]
    dt = float(t['dt'])
with (root / 'picks.csv').open('w', newline='') as output:
    writer = csv.writer(output)
    writer.writerow(['file_name', 'phase', 'pick_idx', 'score'])
    for path in sorted(root.glob('record_*.npz')):
        with np.load(path) as record:
            assert float(record['dt']) == dt
            labels = str(record['channels']).split(',')
            signal = record['data'][:, [labels.index(c) for c in channels]]
        for phase, pattern in patterns:
            v = pattern.ravel()
            scale = np.linalg.norm(v)
            scores = []
            for j in range(signal.shape[0] - pattern.shape[0] + 1):
                w = signal[j:j + len(pattern)].ravel()
                scores.append(float(np.dot(v, w) / (scale * np.linalg.norm(w))))
            index = max(range(len(scores)), key=scores.__getitem__)
            writer.writerow([path.name, phase, index, f'{scores[index]:.4f}'])
PY
python /tmp/solve_template.py
