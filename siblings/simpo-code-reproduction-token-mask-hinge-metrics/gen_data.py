import numpy as np

rng = np.random.default_rng(11)
B, T = 16, 48
logps = rng.uniform(-3.5, -0.05, (2 * B, T))
logps[:B] = np.minimum(logps[:B] + 0.3, -0.01)
labels = np.full((2 * B, T), -100, dtype=np.int32)
for i in range(2 * B):
    p = int(rng.integers(4, 16))
    r = int(rng.integers(8, T - p + 1))
    labels[i, p:p + r] = rng.integers(5, 32000, r)
np.savez("tokens.npz", per_token_logps=logps.astype(np.float32), labels=labels)
