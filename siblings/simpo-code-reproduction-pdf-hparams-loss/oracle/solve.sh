#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import numpy as np
d = np.load("batch.npz")
beta, gamma, ls = 2.5, 1.375, 0.1
cr = beta * d["chosen_logps_sum"] / d["chosen_len"]
rr = beta * d["rejected_logps_sum"] / d["rejected_len"]
z = cr - rr - gamma
loss = (1 - ls) * np.logaddexp(0, -z) + ls * np.logaddexp(0, z)
np.savez("loss.npz", losses=loss.astype(np.float64), chosen_rewards=cr.astype(np.float64), rejected_rewards=rr.astype(np.float64))
EOF
python3 /tmp/solve.py
