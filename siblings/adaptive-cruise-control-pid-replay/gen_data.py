import numpy as np
import yaml

np.random.seed(11)
dt = 0.1
n = 401
cfg = {
    'acc': {'set_speed': 30.0, 'time_headway': 1.5, 'min_distance': 10.0, 'ttc_threshold': 3.0},
    'limits': {'max_accel': 2.5, 'max_decel': -7.0},
    'dt': dt,
    'gains': {'pid_speed': {'kp': 0.6, 'ki': 0.05, 'kd': 0.1},
              'pid_distance': {'kp': 0.25, 'ki': 0.02, 'kd': 0.3}},
}
with open('acc_config.yaml', 'w') as f:
    yaml.safe_dump(cfg, f, sort_keys=False)

t = np.arange(n) * dt
L = np.where(t < 25, 20.0, np.where(t < 27, 20.0 - 6.0 * (t - 25), 8.0))
ego = np.zeros(n)
d = np.zeros(n)
k12 = 120
for k in range(n):
    if k <= k12:
        ego[k] = 10.0 + 18.0 * (1 - np.exp(-t[k] / 3.0))
    else:
        ego[k] = ego[k - 1] + dt / 1.5 * (L[k - 1] - ego[k - 1])
    if k == k12:
        d[k] = 35.0
    elif k > k12:
        d[k] = d[k - 1] + (L[k - 1] - ego[k - 1]) * dt
ego_n = ego + np.random.normal(0, 0.03, n)
lead_n = L + np.random.normal(0, 0.03, n)
d_n = d + np.random.normal(0, 0.05, n)

with open('sensor_log.csv', 'w') as f:
    print('time,ego_speed,lead_speed,distance', file=f)
    for k in range(n):
        if 120 <= k < 350:
            print(f'{t[k]:.1f},{ego_n[k]:.2f},{lead_n[k]:.2f},{d_n[k]:.2f}', file=f)
        else:
            print(f'{t[k]:.1f},{ego_n[k]:.2f},,', file=f)
