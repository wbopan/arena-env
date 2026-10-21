import numpy as np

rng = np.random.default_rng(7321)
cp = [0.0, 0.08, 0.0, 0.15, 0.05]
lines = ['case_id,omega0,omegac,g,kappa,gamma_down,gamma_phi,gamma_cpump']
for i in range(5):
    w0 = round(rng.uniform(0.8, 1.2), 3)
    wc = round(rng.uniform(0.8, 1.2), 3)
    g = round(rng.uniform(0.1, 0.4), 3)
    kappa = round(rng.uniform(0.5, 1.5), 3)
    gd = round(rng.uniform(0.05, 0.2), 3)
    gphi = round(rng.uniform(0.005, 0.05), 4)
    lines.append(f'{i + 1},{w0},{wc},{g},{kappa},{gd},{gphi},{cp[i]}')
with open('cases.csv', 'w') as f:
    f.write('\n'.join(lines) + '\n')
