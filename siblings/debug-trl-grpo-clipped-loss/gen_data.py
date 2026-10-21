import numpy as np

rng = np.random.default_rng(1234)
N, T, V = 8, 6, 12
logits = rng.normal(0.0, 2.0, (N, T, V))
tokens = rng.integers(0, V, (N, T)).astype(np.int64)
lengths = rng.integers(3, T + 1, N)
mask = (np.arange(T)[None, :] < lengths[:, None]).astype(np.int64)
m = logits.max(-1, keepdims=True)
lse = (m + np.log(np.exp(logits - m).sum(-1, keepdims=True)))[..., 0]
sel = np.take_along_axis(logits, tokens[..., None], -1)[..., 0]
lp = sel - lse
old = np.minimum(lp + rng.normal(0.0, 0.25, (N, T)), -1e-6)
ref = np.minimum(lp + rng.normal(0.0, 0.2, (N, T)), -1e-6)
tokens = np.where(mask == 1, tokens, 0)
old = np.where(mask == 1, old, 0.0)
ref = np.where(mask == 1, ref, 0.0)
adv = rng.normal(0.0, 1.0, N)
np.save("logits.npy", logits)
np.save("tokens.npy", tokens)
np.save("mask.npy", mask)
np.save("old_logprobs.npy", old)
np.save("ref_logprobs.npy", ref)
np.save("advantages.npy", adv)
