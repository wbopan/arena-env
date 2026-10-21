#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_masks.py << 'EOF'
import json
import numpy as np
from scipy import ndimage

fr = np.load("frames.npz")["frames"].astype(np.int64)
T, H, W = fr.shape
sh = {d["frame"]: (d["dx"], d["dy"]) for d in json.load(open("shifts.json"))}
yy, xx = np.mgrid[0:H, 0:W]
out = {"shape": np.array([H, W], dtype=np.int32)}
for t in range(T):
    mask = np.zeros((H, W), bool)
    if t > 0:
        dx, dy = sh[t]
        sy, sx = yy - dy, xx - dx
        valid = (sy >= 0) & (sy < H) & (sx >= 0) & (sx < W)
        warped = np.zeros((H, W), np.int64)
        warped[valid] = fr[t - 1][sy[valid], sx[valid]]
        diff = np.abs(fr[t] - warped)
        v = diff[valid]
        med = np.median(v)
        mad = np.median(np.abs(v - med))
        thr = max(20.0, med + 3 * 1.4826 * mad)
        raw = valid & (diff > thr)
        lab, n = ndimage.label(raw, structure=np.ones((3, 3), int))
        sizes = np.bincount(lab.ravel())
        keep = sizes >= 12
        keep[0] = False
        mask = keep[lab]
    rows, cols = np.nonzero(mask)
    out[f"f_{t}_data"] = np.ones(len(cols), np.uint8)
    out[f"f_{t}_indices"] = cols.astype(np.int32)
    out[f"f_{t}_indptr"] = np.concatenate([[0], np.cumsum(np.bincount(rows, minlength=H))]).astype(np.int64)
np.savez("dyn_masks.npz", **out)
EOF
python3 /tmp/solve_masks.py
