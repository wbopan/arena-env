import csv
import numpy as np

rng = np.random.default_rng(1234)
K = float(rng.uniform(0.08, 0.15))
tau = float(rng.uniform(20.0, 45.0))
Ta = float(rng.uniform(16.5, 19.5))
u = float(rng.choice([40.0, 50.0, 60.0, 70.0]))
dt = 0.5
t0 = float(rng.choice([8.0, 10.0, 12.0]))
tend = 180.0

n = int(round(tend / dt)) + 1
with open('calibration.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['time', 'temperature', 'heater_power'])
    for i in range(n):
        t = i * dt
        if t < t0:
            p = 0.0
            Tt = Ta
        else:
            p = u
            Tt = Ta + K * u * (1.0 - np.exp(-(t - t0) / tau))
        w.writerow([round(t, 2), round(Tt + float(rng.normal(0.0, 0.08)), 3), p])
