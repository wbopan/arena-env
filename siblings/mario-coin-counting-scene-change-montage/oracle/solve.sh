#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_montage.py <<'PY'
from pathlib import Path
from PIL import Image, ImageChops

root = Path('/root/work')
frames = [Image.open(root / 'frames' / f'frame_{i:03d}.png').convert('L') for i in range(8)]
chosen = [frames[0]]
for i in range(1, len(frames)):
    difference = ImageChops.difference(frames[i - 1], frames[i])
    mean = sum(difference.getdata()) / (32 * 24)
    if mean >= 25.0:
        chosen.append(frames[i])
montage = Image.new('L', (32 * len(chosen), 24))
for index, frame in enumerate(chosen):
    montage.paste(frame, (32 * index, 0))
montage.save(root / 'scene_montage.png')
PY
python /tmp/solve_montage.py
