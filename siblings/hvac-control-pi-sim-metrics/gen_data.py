import json
import numpy as np

rng = np.random.default_rng(20240607)
K = float(rng.uniform(0.08, 0.15))
tau = float(rng.uniform(20.0, 45.0))
Ta = float(rng.uniform(16.0, 19.0))
T0 = Ta + float(rng.uniform(0.0, 1.0))
sp = float(rng.uniform(21.0, 23.0))
lam = float(rng.uniform(0.3, 0.8)) * tau
Kp = tau / (K * lam) * float(rng.uniform(1.0, 2.0))
Ki = Kp / tau * float(rng.uniform(2.0, 4.0))
T_max = sp + float(rng.uniform(0.6, 1.8))
params = {
    'K': round(K, 4),
    'tau': round(tau, 3),
    'T_ambient': round(Ta, 3),
    'T0': round(T0, 3),
    'setpoint': round(sp, 2),
    'T_max': round(T_max, 2),
    'Kp': round(Kp, 4),
    'Ki': round(Ki, 5),
    'dt': 0.5,
    'duration': 300.0,
    'settle_band': 0.5,
}
with open('params.json', 'w') as f:
    json.dump(params, f, indent=2)
