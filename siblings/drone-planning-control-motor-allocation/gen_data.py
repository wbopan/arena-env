import numpy as np

rng = np.random.default_rng(424242)
mass = float(rng.uniform(0.45, 0.7))
cT = float(rng.uniform(1.1e-8, 1.35e-8))
cQ = float(rng.uniform(6.5e-10, 8.5e-10))
d = float(rng.uniform(0.15, 0.2))
with open('system_params.yaml', 'w') as f:
    f.write('mass: %.3f\n' % mass)
    f.write('gravity: 9.81\n')
    f.write('cT: %.4e\n' % cT)
    f.write('cQ: %.4e\n' % cQ)
    f.write('arm_length: %.3f\n' % d)
    f.write('rpm_min: 3000\n')
    f.write('rpm_max: 20000\n')
    f.write('sample_rate: 200\n')
N = 40
with open('commands.csv', 'w') as f:
    f.write('id,F,Mx,My,Mz\n')
    for i in range(N):
        F = rng.uniform(0.8, 24.0)
        Mx = rng.normal(0, 0.12)
        My = rng.normal(0, 0.12)
        Mz = rng.normal(0, 0.03)
        f.write('%d,%.6f,%.6f,%.6f,%.6f\n' % (i + 1, F, Mx, My, Mz))
