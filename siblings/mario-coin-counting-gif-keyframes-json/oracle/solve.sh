#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
import numpy as np
from PIL import Image
from scipy import ndimage

im = Image.open("level.gif")
n = im.n_frames
rgbs, lums, durs = [], [], []
for i in range(n):
    im.seek(i)
    rgb = np.array(im.convert("RGB"), dtype=np.int64)
    durs.append(int(im.info.get("duration", 0)))
    rgbs.append(rgb)
    a = rgb.astype(float)
    lums.append(0.299*a[...,0] + 0.587*a[...,1] + 0.114*a[...,2])
keys = [0]
for i in range(1, n):
    if np.abs(lums[i] - lums[keys[-1]]).mean() > 30:
        keys.append(i)
res = []
for k in keys:
    mask = np.all(rgbs[k] == [252, 188, 60], axis=-1)
    _, nc = ndimage.label(mask, structure=np.ones((3, 3)))
    res.append({"index": k, "timestamp_ms": int(sum(durs[:k])), "coins": int(nc)})
with open("keyframes.json", "w") as f:
    json.dump({"n_frames": n, "keyframes": res}, f, indent=2)
EOF
python3 /tmp/solve.py
