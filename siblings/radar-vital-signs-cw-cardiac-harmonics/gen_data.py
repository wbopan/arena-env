import json
from pathlib import Path

import numpy as np

rng = np.random.default_rng(51083)
fs, n = 32, 1024
settings = [(1.125, 0.24, 0.33, 0.1875), (1.25, 0.35, 0.19, 0.21875), (1.375, 0.23, 0.29, 0.28125)]
for j, (heart, fundamental, harmonic, breath) in enumerate(settings, 1):
    name = f'pulse_{j:02d}'
    t = np.arange(n) / fs
    phase = (2 * np.pi * 0.125 * t + 0.33 * np.sin(2 * np.pi * breath * t + 0.12 * j)
             + fundamental * np.sin(2 * np.pi * heart * t + 0.15 * j)
             + harmonic * np.sin(2 * np.pi * 2 * heart * t + 0.31 * j)
             + rng.normal(0, 0.003, n))
    z = 10500 * np.exp(1j * phase) + (3200 - 2700j)
    pairs = np.empty(2 * n, dtype='<i2')
    pairs[::2] = np.rint(z.real).astype('<i2')
    pairs[1::2] = np.rint(z.imag).astype('<i2')
    pairs.tofile(name + '.bin')
    Path(name + '.json').write_text(json.dumps({'format': 'int16_le_interleaved_complex', 'sample_rate_hz': fs, 'sample_count': n}) + '\n')
