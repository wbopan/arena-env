#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_rot.py <<'EOF'
import csv
import numpy as np

F = 0.05 + 0.0005 * np.arange(3901)
data = {}
with open('stars_lc.csv') as fh:
    for r in csv.DictReader(fh):
        if int(r['quality']) != 0:
            continue
        data.setdefault(r['star_id'], []).append((float(r['time']), float(r['flux'])))
with open('rotation.csv', 'w') as out:
    print('star_id,period_days,amplitude', file=out)
    for sid in sorted(data):
        a = np.array(data[sid])
        t = a[:, 0]
        y = a[:, 1]
        w = 2 * np.pi * F[:, None] * t[None, :]
        X = np.stack([np.sin(w), np.cos(w), np.ones_like(w)], axis=2)
        M = np.einsum('fni,fnj->fij', X, X)
        b = np.einsum('fni,n->fi', X, y)
        coef = np.linalg.solve(M, b[:, :, None])[:, :, 0]
        pred = np.einsum('fni,fi->fn', X, coef)
        rss = ((y[None, :] - pred) ** 2).sum(axis=1)
        tss = ((y - y.mean()) ** 2).sum()
        p = 1 - rss / tss
        i = int(np.argmax(p))
        print('%s,%.4f,%.5f' % (sid, 1 / F[i], np.hypot(coef[i, 0], coef[i, 1])), file=out)
EOF
python3 /tmp/solve_rot.py
