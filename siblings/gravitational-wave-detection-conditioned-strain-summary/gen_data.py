import numpy as np

rng = np.random.default_rng(314159)
fs = 1024
n = 2048
t = np.arange(n) / fs
raw = (0.45 * np.sin(2 * np.pi * 8 * t)
       + 0.19 * np.sin(2 * np.pi * (48 * t + 15 * t * t))
       + 0.11 * np.sin(2 * np.pi * 113 * t)
       + 0.17 * rng.normal(size=n))
raw += 0.65 * np.exp(-((t - 1.24) / 0.018) ** 2) * np.sin(2 * np.pi * 90 * t)
np.save('raw_strain.npy', raw)
