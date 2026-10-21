#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json
import numpy as np
d = np.load('data.npz'); X, y, w = d['X'], d['y'], d['w0'].copy()
c = json.load(open('config.json')); lam = c['l2']
def loss(w):
    return float(np.mean(np.logaddexp(0, -y * (X @ w))) + 0.5 * lam * np.dot(w, w))
def grad(w):
    m = y * (X @ w)
    sig = np.exp(-np.logaddexp(0, m))
    return X.T @ (-y * sig) / len(y) + lam * w
res = {'loss_init': loss(w), 'grad_init': grad(w).tolist()}
for _ in range(c['steps']):
    w = w - c['lr'] * grad(w)
res['w_final'] = w.tolist()
res['loss_final'] = loss(w)
res['train_accuracy'] = float(np.mean(np.where(X @ w >= 0, 1.0, -1.0) == y))
json.dump(res, open('result.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
