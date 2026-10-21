#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, glob, os
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image

def luma(p):
    a = np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)
    return 0.299*a[...,0] + 0.587*a[...,1] + 0.114*a[...,2]

def count(img, t):
    w = sliding_window_view(img, t.shape)
    tz = t - t.mean()
    wz = w - w.mean(axis=(2,3), keepdims=True)
    num = (wz*tz).sum(axis=(2,3))
    den = np.sqrt((wz*wz).sum(axis=(2,3)) * (tz*tz).sum())
    s = np.where(den > 1e-9, num/np.where(den > 1e-9, den, 1), 0.0)
    ys, xs = np.nonzero(s >= 0.9)
    kept = []
    for _, y, x in sorted(zip(s[ys,xs], ys, xs), key=lambda q: -q[0]):
        if all(max(abs(y-a), abs(x-b)) > 3 for a, b in kept):
            kept.append((y, x))
    return len(kept)

coin = luma("coin.png"); goomba = luma("goomba.png")
with open("counts.csv", "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["frame_id", "coins", "goombas"])
    for p in sorted(glob.glob("frames/frame_*.png")):
        img = luma(p)
        wr.writerow([os.path.basename(p), count(img, coin), count(img, goomba)])
EOF
python3 /tmp/solve.py
