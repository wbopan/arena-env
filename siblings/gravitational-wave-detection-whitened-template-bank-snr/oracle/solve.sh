#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
import numpy as np
d = np.load("data.npy").astype(np.float64)
T = np.load("templates.npy").astype(np.float64)
res = []
for i, h in enumerate(T):
    rho = np.correlate(d, h, mode="valid") / np.sqrt(np.sum(h * h))
    k = int(np.argmax(np.abs(rho)))
    res.append({"index": i, "peak_snr": round(float(abs(rho[k])), 3), "peak_time_s": round(k / 512.0, 4), "_raw": float(abs(rho[k]))})
best = int(np.argmax([r["_raw"] for r in res]))
for r in res:
    del r["_raw"]
with open("/root/work/results.json", "w") as f:
    json.dump({"templates": res, "best_index": best}, f, indent=2)
EOF
python3 /tmp/solve.py
