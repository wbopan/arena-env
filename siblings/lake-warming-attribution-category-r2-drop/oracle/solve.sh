#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import numpy as np
import pandas as pd

D = '/root/work/'
df = pd.read_csv(D + 'water_temperature.csv')
for f in ['climate.csv', 'hydrology.csv', 'land_cover.csv']:
    df = df.merge(pd.read_csv(D + f), on='Year')
df['NetRadiation'] = df['Shortwave'] + df['Longwave']
cats = {'Heat': ['AirTemp', 'NetRadiation', 'Humidity'],
        'Flow': ['Precip', 'Inflow', 'Outflow'],
        'Wind': ['WindSpeed'],
        'Human': ['DevelopedArea', 'AgricultureArea']}
y = df['WaterTemp'].to_numpy(float)

def r2(cols):
    X = np.column_stack([np.ones(len(df)), df[cols].to_numpy(float)])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    return 1 - (e @ e) / np.sum((y - y.mean()) ** 2)

allv = sum(cats.values(), [])
full = r2(allv)
out = [(c, round((full - r2([v for v in allv if v not in vs])) * 100, 2)) for c, vs in cats.items()]
out.sort(key=lambda t: -t[1])
pd.DataFrame(out, columns=['category', 'contribution']).to_csv(D + 'contributions.csv', index=False)
EOF
python3 /tmp/solve.py
