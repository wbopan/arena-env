import numpy as np

rng = np.random.default_rng(31415)
rows = []
for k in range(6):
    sid = 'STAR%02d' % (k + 1)
    P = rng.uniform(1.2, 9.5)
    A = rng.uniform(0.008, 0.03)
    ph = rng.uniform(0, 2 * np.pi)
    n = 75
    t = 1500.0 + np.sort(rng.uniform(0, 30, n))
    f = (1.0 + A * np.sin(2 * np.pi * t / P + ph)
         + 0.25 * A * np.sin(4 * np.pi * t / P + 1.3 * ph)
         + rng.normal(0, 0.003, n))
    q = np.zeros(n, dtype=int)
    bad = rng.choice(n, 6, replace=False)
    q[bad] = rng.choice([1, 4, 32, 128, 1024], 6)
    f[bad] += rng.choice([-1.0, 1.0], 6) * rng.uniform(0.05, 0.25, 6)
    for ti, fi, qi in zip(t, f, q):
        rows.append((float(ti), sid, float(fi), int(qi)))
rows.sort()
with open('stars_lc.csv', 'w') as fh:
    print('star_id,time,flux,quality', file=fh)
    for ti, sid, fi, qi in rows:
        print('%s,%.5f,%.6f,%d' % (sid, ti, fi, qi), file=fh)
