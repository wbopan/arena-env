import json
import numpy as np

rng = np.random.default_rng(20240611)
dt = 0.05
n = 120
t = np.arange(n) * dt
zetas = [0.35, 0.6, 0.85, 0.25]
wns = [3.0, 2.2, 1.6, 0.9]
rows = []
targets = {}
for i in range(4):
    fid = i + 1
    start = rng.uniform(-2.0, 2.0, 3)
    start[2] = abs(start[2]) + 0.5
    target = start + rng.uniform(-3.0, 3.0, 3)
    z = zetas[i]
    pos = []
    for ax in range(3):
        w = wns[i] * (1.0 + 0.12 * ax)
        wd = w * np.sqrt(1 - z * z)
        e = np.exp(-z * w * t) * (np.cos(wd * t) + z / np.sqrt(1 - z * z) * np.sin(wd * t))
        p = target[ax] + (start[ax] - target[ax]) * e + rng.normal(0, 0.001, n)
        pos.append(p)
    targets[str(fid)] = [round(float(v), 4) for v in target]
    for k in range(n):
        rows.append('%d,%.2f,%.4f,%.4f,%.4f' % (fid, t[k], pos[0][k], pos[1][k], pos[2][k]))
order = rng.permutation(len(rows))
with open('flights.csv', 'w') as f:
    f.write('flight_id,t,x,y,z\n')
    for j in order:
        f.write(rows[j] + '\n')
with open('targets.json', 'w') as f:
    json.dump(targets, f, indent=2)
