#!/usr/bin/env bash
set -euo pipefail
cat > /root/work/solve_descriptions.py <<'PY'
import csv
from pathlib import Path

root = Path('/root/work')
with (root / 'ppdev_commands.csv').open(newline='') as f:
    rows = list(csv.DictReader(f))
lines = [
    'include <linux/ppdev.h>',
    'include <linux/parport.h>',
    '',
    'resource fd_ppdev[fd]',
    '',
    'ppdev_frob_struct {',
    '    mask int8',
    '    val int8',
    '}',
    '',
    'syz_open_dev$ppdev(dev ptr[in, string["/dev/parport#"]], id intptr, flags flags[open_flags]) fd_ppdev',
    '',
]
for row in rows:
    name = row['name']
    declaration = f'ioctl${name}(fd fd_ppdev, cmd const[{name}]'
    if row['argument'] != 'none':
        typ = 'ppdev_frob_struct' if row['argument'] == 'frob' else row['argument']
        declaration += f", arg ptr[{row['direction']}, {typ}]"
    lines.append(declaration + ')')
(root / 'dev_training.txt').write_text('\n'.join(lines) + '\n')
PY
python3 /root/work/solve_descriptions.py
