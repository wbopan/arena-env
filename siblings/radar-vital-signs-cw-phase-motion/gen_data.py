import json
from pathlib import Path

import numpy as np

rng = np.random.default_rng(29471)
fs = 20
n = 600
fc = 24_125_000_000
for j in range(1, 4):
    name = f'motion_{j:02d}'
    t = np.arange(n) / fs
    breath = [0.20, 0.23333333333333334, 0.16666666666666666][j - 1]
    phase = (2 * np.pi * 0.21 * t + (0.47 + 0.13 * j) * np.sin(2 * np.pi * breath * t + 0.2 * j)
             + 0.055 * np.sin(2 * np.pi * (1.0 + 0.1 * j) * t)
             + rng.normal(0, 0.009, n))
    iq = 1.7 * np.exp(1j * phase) + (2.2 - 1.3j)
    iq += rng.normal(0, 0.002, n) + 1j * rng.normal(0, 0.002, n)
    pairs = np.empty(2 * n, dtype='<f4')
    pairs[0::2], pairs[1::2] = iq.real, iq.imag
    pairs.tofile(name + '.bin')
    Path(name + '.json').write_text(json.dumps({'format': 'complex64_le_interleaved', 'sample_rate_hz': fs, 'sample_count': n, 'carrier_frequency_hz': fc}) + '\n')
