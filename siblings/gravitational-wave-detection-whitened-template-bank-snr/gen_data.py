import numpy as np

rng = np.random.default_rng(20240611)
fs = 512
N = 2048
M = 128
t = np.arange(M) / fs
tc = M / fs + 0.004

taper = np.ones(M)
r1 = 16
r2 = 8
taper[:r1] = 0.5 * (1 - np.cos(np.pi * np.arange(r1) / r1))
taper[-r2:] = 0.5 * (1 + np.cos(np.pi * (np.arange(r2) + 1) / r2))

templates = []
for f0 in [30, 38, 46, 54, 62, 70]:
    tau = np.clip(1 - t / tc, 1e-3, None)
    f = np.minimum(f0 * tau ** (-3.0 / 8.0), 240.0)
    phase = 2 * np.pi * np.cumsum(f) / fs + rng.uniform(0, 2 * np.pi)
    amp = (f / f0) ** (2.0 / 3.0)
    h = rng.uniform(0.5, 2.0) * amp * taper * np.cos(phase)
    templates.append(h)
templates = np.array(templates, dtype=np.float64)

inj = int(rng.integers(0, 6))
off = int(rng.integers(200, N - M - 200))
target = rng.uniform(8.0, 11.0)
h = templates[inj]
data = rng.normal(size=N)
data[off:off + M] += target * h / np.sqrt(np.sum(h * h))

np.save("data.npy", data.astype(np.float64))
np.save("templates.npy", templates)
