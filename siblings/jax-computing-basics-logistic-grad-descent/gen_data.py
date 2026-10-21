import json
import numpy as np

rng = np.random.default_rng(1337)
N, D = 240, 6
X = rng.normal(size=(N, D))
X[:, 0] *= 8.0  # large-scale feature -> large margins
w_true = rng.normal(size=D)
logits = X @ w_true
p = 1.0 / (1.0 + np.exp(-logits))
y = np.where(rng.random(N) < p, 1.0, -1.0)
w0 = rng.normal(scale=0.5, size=D)
w0[0] = 3.0
np.savez("data.npz", X=X, y=y, w0=w0)
with open("config.json", "w") as f:
    json.dump({"lr": 0.05, "steps": 37, "l2": 0.02}, f)
