#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json
import numpy as np
d = np.load("tokens.npz")
lp = d["per_token_logps"].astype(np.float64)
mask = d["labels"] != -100
avg = np.where(mask, lp, 0.0).sum(1) / mask.sum(1)
B = lp.shape[0] // 2
beta, gbr = 2.0, 0.5
c, r = avg[:B], avg[B:]
losses = np.maximum(0.0, 1.0 - beta * ((c - r) - gbr))
cr, rr = beta * c, beta * r
out = {
    "losses": [round(float(x), 6) for x in losses],
    "mean_loss": round(float(losses.mean()), 6),
    "reward_accuracy": round(float((cr > rr).mean()), 6),
    "reward_margin_mean": round(float((cr - rr).mean()), 6),
    "chosen_rewards_mean": round(float(cr.mean()), 6),
}
json.dump(out, open("metrics.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
