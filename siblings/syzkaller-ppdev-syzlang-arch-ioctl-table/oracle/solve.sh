#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve_numbers.py <<'PY'
import csv
from pathlib import Path

root = Path('/root/work')
with (root / 'ioctl_layout.csv').open(newline='') as f:
    rows = list(csv.DictReader(f))
codes = {'IO': 0, 'IOW': 1, 'IOR': 2, 'IOWR': 3}
with (root / 'ioctl_numbers.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', '386', 'amd64'])
    for row in rows:
        base = (codes[row['direction']] << 30) | (int(row['type'], 16) << 8) | int(row['nr'], 16)
        writer.writerow([row['name'], base | (int(row['size_386']) << 16), base | (int(row['size_amd64']) << 16)])
PY
python3 /root/work/solve_numbers.py
