from pathlib import Path
import numpy as np

rng = np.random.default_rng(7319)
root = Path.cwd()
channels = ['BHE', 'BHN', 'BHZ']
p = rng.normal(size=(24, 3)).astype('float32')
s = rng.normal(size=(24, 3)).astype('float32')
np.savez(root / 'templates.npz', p_template=p, s_template=s, channels=','.join(channels), dt=0.02)
for i in range(4):
    x = rng.normal(0, 0.025, (220, 3)).astype('float32')
    pi = int(rng.integers(25, 65))
    si = int(rng.integers(120, 165))
    x[pi:pi + 24] += (0.9 + i * 0.16) * p
    x[si:si + 24] += (1.3 - i * 0.09) * s
    order = rng.permutation(3)
    np.savez(root / f'record_{i:02d}.npz', data=x[:, order], channels=','.join(channels[j] for j in order), dt=0.02)
