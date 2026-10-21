import numpy as np

rng = np.random.default_rng(20240607)
B, T, D, H = 5, 18, 4, 7
seq = rng.normal(size=(B, T, D))
lengths = np.array([18, 11, 5, 15, 1], dtype=np.int64)
# put garbage in padded positions so they must be masked, not just ignored by chance
for i in range(B):
    seq[i, lengths[i]:] = rng.normal(scale=5.0, size=(T - lengths[i], D))
Wx = rng.normal(scale=0.6, size=(D, H))
Wh = rng.normal(scale=0.45, size=(H, H))
b = rng.normal(scale=0.2, size=H)
h0 = rng.normal(scale=0.3, size=(B, H))
np.save("seq.npy", seq)
np.save("lengths.npy", lengths)
np.savez("rnn_params.npz", Wx=Wx, Wh=Wh, b=b, h0=h0)
