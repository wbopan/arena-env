import csv
from pathlib import Path
import numpy as np

rng = np.random.default_rng(8042)
root = Path.cwd()
labels = ['EHN', 'EHZ', 'EHE']
rows = []
for i in range(4):
    name = f'station_{i:02d}.npz'
    data = rng.normal(0, 0.035, (300, 3)).astype('float32')
    p0 = 10 + 3 * i
    s0 = p0 + 140
    t = np.arange(100) * 0.01
    low = np.sin(2 * np.pi * 3 * t)
    high = np.sin(2 * np.pi * 14 * t)
    data[p0:p0 + 100, 1] += ((1.0 + 0.2 * i) * low + (0.25 + 0.1 * i) * high).astype('float32')
    data[s0:s0 + 100, 0] += ((0.55 + 0.07 * i) * low + 1.2 * high).astype('float32')
    data[s0:s0 + 100, 2] += (0.8 * low + (0.45 + 0.08 * i) * high).astype('float32')
    data[s0:s0 + 100, 1] += (0.3 * low + 0.14 * high).astype('float32')
    order = rng.permutation(3)
    np.savez(root / name, data=data[:, order], channels=','.join(labels[j] for j in order), dt=0.01)
    rows.extend([(name, 'P', p0, p0 + 100), (name, 'S', s0, s0 + 100)])
with (root / 'windows.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['file_name', 'phase', 'start_idx', 'end_idx'])
    writer.writerows(rows)
