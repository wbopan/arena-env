import numpy as np
import yaml

np.random.seed(42)
dt = 0.2
n = 451
set_speed = 30.0
cfg = {'acc_settings': {'set_speed': set_speed, 'time_headway': 1.5, 'min_distance': 10.0},
       'simulation': {'dt': dt}}
with open('sim_config.yaml', 'w') as f:
    yaml.safe_dump(cfg, f, sort_keys=False)

t = np.arange(n) * dt
z, wn = 0.6, 0.45
wd = wn * np.sqrt(1 - z * z)
phi = np.arccos(z)
k0 = 200
ego = np.zeros(n)
lead = np.full(n, np.nan)
dist = np.full(n, np.nan)
for k in range(k0):
    ego[k] = set_speed * (1 - np.exp(-z * wn * t[k]) / np.sqrt(1 - z * z) * np.sin(wd * t[k] + phi))
d = 70.0
for k in range(k0, n):
    if k > k0:
        ego[k] = ego[k - 1] + dt / 3.0 * (lead[k - 1] - ego[k - 1])
        d = d + (lead[k - 1] - ego[k - 1]) * dt
    else:
        ego[k] = ego[k - 1]
    lead[k] = 24.0 + 1.5 * np.sin(0.2 * (t[k] - 40.0))
    dist[k] = d
ego_n = np.clip(ego + np.random.normal(0, 0.05, n), 0, None)
lead_n = lead + np.random.normal(0, 0.05, n)
dist_n = dist + np.random.normal(0, 0.1, n)

with open('drive_log.csv', 'w') as f:
    print('time,ego_speed,lead_speed,distance', file=f)
    for k in range(n):
        if np.isnan(lead[k]):
            print(f'{t[k]:.1f},{ego_n[k]:.3f},,', file=f)
        else:
            print(f'{t[k]:.1f},{ego_n[k]:.3f},{lead_n[k]:.3f},{dist_n[k]:.3f}', file=f)
