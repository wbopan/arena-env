import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
lakes = {'L01': 0.05, 'L02': 0.0, 'L03': -0.035, 'L04': 0.015, 'L05': 0.08, 'L06': -0.005}
rows = []
for lid, s in lakes.items():
    base = rng.uniform(12, 22)
    for y in range(1991, 2021):
        t = base + s * (y - 1991) + rng.normal(0, 0.4)
        rows.append({'lake_id': lid, 'year': y, 'temp_c': round(float(t), 1)})
df = pd.DataFrame(rows)
mask = rng.random(len(df)) < 0.1
df.loc[mask, 'temp_c'] = np.nan
df = df.sample(frac=1.0, random_state=3).reset_index(drop=True)
df.to_csv('lake_temps.csv', index=False)
