import math
import numpy as np

rng = np.random.default_rng(20240611)
Nc = 8
weights = np.exp(-np.arange(Nc) / 2.5)
kets = []
beta = 0.9 + 0.6j
coh = np.array([np.exp(-abs(beta) ** 2 / 2) * beta ** n / math.sqrt(math.factorial(n)) for n in range(Nc)])
coh = coh / np.linalg.norm(coh)
q = np.array([np.cos(0.4), np.sin(0.4) * np.exp(0.7j)])
kets.append(np.kron(coh, q))
for _ in range(2):
    c = (rng.normal(size=(Nc, 2)) + 1j * rng.normal(size=(Nc, 2))) * weights[:, None]
    v = c.reshape(-1)
    v = v / np.linalg.norm(v)
    kets.append(v)
p = rng.dirichlet([2.0, 2.0, 2.0])
rho = sum(pi * np.outer(k, k.conj()) for pi, k in zip(p, kets))
rho = rho / np.trace(rho).real
rho = 0.5 * (rho + rho.conj().T)
np.savetxt('rho_real.csv', rho.real, delimiter=',', fmt='%.15e')
np.savetxt('rho_imag.csv', rho.imag, delimiter=',', fmt='%.15e')
