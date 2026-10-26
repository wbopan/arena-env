import json
from pathlib import Path

import numpy as np

rng = np.random.default_rng(83042)
rate, count, fast = 32, 1024, 8
for j, target_bin in [(1, 2), (2, 3)]:
    name = f'sweep_{j:02d}'
    t = np.arange(count) / rate
    x = np.arange(fast)
    phase = (0.14 * t + (0.70 + j * 0.13) * np.sin(2 * np.pi * (0.1875 if j == 1 else 0.25) * t + j * 0.35)
             + 0.06 * np.sin(2 * np.pi * 1.125 * t))
    adc = (10500 + 5800 * np.cos(2 * np.pi * target_bin * x[None, :] / fast + phase[:, None])
           + 2300 * np.cos(2 * np.pi * x[None, :] / fast + 0.4)
           + rng.normal(0, 18, (count, fast)))
    np.rint(adc).astype('<i2').tofile(name + '.bin')
    Path(name + '.json').write_text(json.dumps({'format': 'int16_le_real_only', 'samples_per_chirp': fast, 'chirp_count': count, 'chirp_rate_hz': rate, 'carrier_frequency_hz': 60_000_000_000, 'range_per_bin_m': 0.3}) + '\n')
