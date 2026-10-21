import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(424242)
VP = 6.0
VS = VP / 1.75
DEPTH = 10.0
BASE = datetime(2019, 7, 4, 19, 0, 0)


def iso(t):
    return (BASE + timedelta(seconds=round(float(t), 3))).isoformat(timespec='milliseconds')


n_sta = 10
lat = np.round(35.70 + rng.uniform(-0.35, 0.35, n_sta), 5)
lon = np.round(-117.50 + rng.uniform(-0.45, 0.45, n_sta), 5)
el = np.round(rng.uniform(200, 1800, n_sta))
lat0 = lat.mean()
lon0 = lon.mean()
sx = (lon - lon0) * 111.19 * np.cos(np.radians(lat0))
sy = (lat - lat0) * 111.19

rows = []
for i in range(n_sta):
    for ch in ('BHE', 'BHN', 'BHZ'):
        rows.append({'network': 'CI', 'station': f'ST{i:02d}', 'channel': ch,
                     'longitude': lon[i], 'latitude': lat[i], 'elevation_m': el[i],
                     'response': round(float(rng.uniform(1e8, 1e9)), 1)})
st = pd.DataFrame(rows)
st = st.iloc[rng.permutation(len(st))]
st.to_csv('stations.csv', index=False)

n_ev = 5
picks = []
for e in range(n_ev):
    ex, ey = rng.uniform(-20, 20, 2)
    t0 = 30 + 60 * e + rng.uniform(0, 10)
    for i in range(n_sta):
        d = np.sqrt((ex - sx[i]) ** 2 + (ey - sy[i]) ** 2 + (DEPTH + el[i] / 1000.0) ** 2)
        for ph, v in (('P', VP), ('S', VS)):
            if rng.random() < 0.1:
                continue
            t = t0 + d / v + rng.normal(0, 0.05)
            picks.append({'event_id': e + 1, 'network': 'CI', 'station': f'ST{i:02d}',
                          'phase': ph, 'timestamp': iso(t)})
pk = pd.DataFrame(picks)
pk = pk.iloc[rng.permutation(len(pk))]
pk.to_csv('picks.csv', index=False)
