#!/bin/bash
set -e
cat > /root/work/solve_lags.py <<'PY'
import csv
from pathlib import Path
import numpy as np
root = Path('/root/work')

def load(filename, field):
    with (root / filename).open(newline='') as f:
        return {int(row['Year']): float(row[field]) for row in csv.DictReader(f)}

water = load('water_temperature.csv', 'WaterTemp')
years = range(2004, 2033)
y = np.array([water[t] - water[t - 1] for t in years])
sources = [('Heat', 'AirTemp', 'climate.csv'), ('Flow', 'Inflow', 'hydrology.csv'), ('Wind', 'WindSpeed', 'climate.csv'), ('Human', 'DevelopedPct', 'land_cover.csv')]
with (root / 'lagged_associations.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['category', 'driver', 'lag_years', 'pearson_r', 'abs_r_pct'])
    for category, driver, filename in sources:
        series = load(filename, driver)
        correlations = []
        for lag in range(3):
            x = np.array([series[t - lag] - series[t - lag - 1] for t in years])
            correlations.append(float(np.corrcoef(x, y)[0, 1]))
        lag = max(range(3), key=lambda i: abs(correlations[i]))
        r = correlations[lag]
        writer.writerow([category, driver, lag, f'{r:.6f}', f'{100 * abs(r):.6f}'])
PY
python /root/work/solve_lags.py
