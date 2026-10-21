import numpy as np

rng = np.random.default_rng(4242)
dt = 40.0 / 1440.0
t = 3000.0 + np.arange(0.0, 14.0, dt)
t = t[~((t > 3006.8) & (t < 3007.8))]
n = len(t)
P = rng.uniform(1.8, 3.3)
t0 = 3000.0 + rng.uniform(0.1, P)
dur = 0.14
depth = 0.008
Prot = rng.uniform(4.5, 6.5)
ph1, ph2 = rng.uniform(0, 2 * np.pi, 2)
f = (1.0 + 0.012 * np.sin(2 * np.pi * t / Prot + ph1)
     + 0.004 * np.sin(4 * np.pi * t / Prot + ph2)
     + 0.003 * (t - 3000.0) / 14.0)
phase = (t - t0 + 0.5 * P) % P - 0.5 * P
f[np.abs(phase) < 0.5 * dur] -= depth
f += rng.normal(0, 0.0008, n)
err = 0.0008 * rng.uniform(0.95, 1.05, n)
q = np.zeros(n, dtype=int)
bad = rng.choice(n, 15, replace=False)
q[bad] = rng.choice([1, 2, 8, 128, 2048], 15)
f[bad] += rng.choice([-1.0, 1.0], 15) * rng.uniform(0.02, 0.1, 15)
cand = np.setdiff1d(np.arange(n), bad)
cand = cand[np.abs(phase[cand]) > 0.3]
fl = rng.choice(cand, 4, replace=False)
f[fl] += rng.uniform(0.01, 0.03, 4)
with open('tess_lc.txt', 'w') as fh:
    print('# time flux quality flux_err', file=fh)
    for a, b, c, d in zip(t, f, q, err):
        print('%.5f %.6f %d %.6f' % (a, b, c, d), file=fh)
