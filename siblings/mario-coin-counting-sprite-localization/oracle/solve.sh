#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_locations.py <<'PY'
import csv
from pathlib import Path
from PIL import Image

root = Path('/root/work')
names = ('coin', 'enemy', 'turtle')
references = {name: Image.open(root / (name + '.png')).convert('L').tobytes() for name in names}
rows = []
for number in (1, 2):
    filename = f'frame_{number:03d}.png'
    frame = Image.open(root / 'frames' / filename).convert('L')
    for y in range(frame.height - 4):
        for x in range(frame.width - 4):
            pixels = frame.crop((x, y, x + 5, y + 5)).tobytes()
            for name in names:
                if pixels == references[name]:
                    rows.append((filename, x, y, name))
rows.sort(key=lambda row: (row[0], row[2], row[1]))
with (root / 'sprite_locations.csv').open('w', newline='', encoding='utf-8') as output:
    writer = csv.writer(output)
    writer.writerow(('frame', 'x', 'y', 'kind'))
    writer.writerows(rows)
PY
python /tmp/solve_locations.py
