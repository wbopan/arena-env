#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import numpy as np
seq = np.load('seq.npy')
L = np.load('lengths.npy')
p = np.load('rnn_params.npz')
Wx, Wh, b, h = p['Wx'], p['Wh'], p['b'], p['h0'].copy()
B, T, _ = seq.shape
out = np.zeros((B, T, Wh.shape[0]))
for t in range(T):
    hn = np.tanh(seq[:, t] @ Wx + h @ Wh + b)
    m = (t < L)[:, None]
    h = np.where(m, hn, h)
    out[:, t] = np.where(m, hn, 0.0)
np.save('hseq.npy', out.astype(np.float64))
EOF
python3 /tmp/solve.py
