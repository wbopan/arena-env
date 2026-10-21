#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
import numpy as np
from scipy.special import log_softmax

lg = np.load('logits.npy')
tok = np.load('tokens.npy')
mask = np.load('mask.npy').astype(float)
old = np.load('old_logprobs.npy')
ref = np.load('ref_logprobs.npy')
adv = np.load('advantages.npy')
lp = np.take_along_axis(log_softmax(lg, axis=-1), tok[..., None], -1)[..., 0]
ratio = np.exp(lp - old)
A = adv[:, None]
surr = np.minimum(ratio * A, np.clip(ratio, 0.8, 1.2) * A)
kl = lp - ref
cnt = mask.sum(1)
S = ((surr * mask).sum(1) / cnt).mean()
K = ((kl * mask).sum(1) / cnt).mean()
clipped = ((ratio < 0.8) | (ratio > 1.2)) & (mask > 0)
out = {
    'seq_logprobs': [float(x) for x in (lp * mask).sum(1)],
    'policy_loss': float(-S),
    'kl': float(K),
    'loss': float(-S + 0.04 * K),
    'clip_fraction': float(clipped.sum() / mask.sum()),
}
with open('loss.json', 'w') as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve.py
