import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(20240501)
VP = 6.0
VS = VP / 1.75
BASE = datetime(2021, 3, 14, 6, 0, 0)


def iso(t):
    return (BASE + timedelta(seconds=round(float(t), 3))).isoformat(timespec='milliseconds')


n_sta = 12
sx = np.round(rng.uniform(-40, 40, n_sta), 3)
sy = np.round(rng.uniform(-40, 40, n_sta), 3)
el = np.round(rng.uniform(0, 1500, n_sta))
ids = [f'CI.S{i:02d}' for i in range(n_sta)]

n_ev = 7
ex = np.round(rng.uniform(-30, 30, n_ev), 2)
ey = np.round(rng.uniform(-30, 30, n_ev), 2)
ez = np.round(rng.uniform(3, 15, n_ev), 2)
et = np.round(5 + np.cumsum(rng.uniform(10, 25, n_ev)), 3)


def pred(e, s, ph):
    d = np.sqrt((ex[e] - sx[s]) ** 2 + (ey[e] - sy[s]) ** 2 + (ez[e] + el[s] / 1000.0) ** 2)
    return et[e] + d / (VP if ph == 'P' else VS)


picks = []
for e in range(n_ev):
    for s in range(n_sta):
        for ph in ('P', 'S'):
            if rng.random() > 0.85:
                continue
            obs = round(pred(e, s, ph) + float(np.clip(rng.normal(0, 0.1), -0.3, 0.3)), 3)
            r = abs(obs - pred(e, s, ph))
            others = [abs(obs - pred(k, s, ph)) for k in range(n_ev) if k != e]
            if min(others) < r + 0.5:
                continue
            picks.append((ids[s], ph, obs))

count = 0
while count < 35:
    s = int(rng.integers(n_sta))
    ph = 'P' if rng.random() < 0.5 else 'S'
    t = round(float(rng.uniform(0, et[-1] + 40)), 3)
    if min(abs(t - pred(k, s, ph)) for k in range(n_ev)) > 1.5:
        picks.append((ids[s], ph, t))
        count += 1

picks.sort(key=lambda p: p[2])
pk = pd.DataFrame({
    'pick_id': [f'P{i + 1:04d}' for i in range(len(picks))],
    'station_id': [p[0] for p in picks],
    'phase': [p[1] for p in picks],
    'timestamp': [iso(p[2]) for p in picks],
    'prob': np.round(rng.uniform(0.3, 0.99, len(picks)), 3),
})
pk.to_csv('picks.csv', index=False)

pd.DataFrame({'station_id': ids, 'x_km': sx, 'y_km': sy, 'elevation_m': el}).to_csv('stations.csv', index=False)
pd.DataFrame({'event_id': np.arange(1, n_ev + 1), 'time': [iso(t) for t in et],
              'x_km': ex, 'y_km': ey, 'z_km': ez}).to_csv('events.csv', index=False)
