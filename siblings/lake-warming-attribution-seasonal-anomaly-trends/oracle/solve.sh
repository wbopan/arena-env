#!/bin/bash
set -e
cat > /root/work/solve_seasons.py <<'PY'
import csv
import json
from pathlib import Path
from scipy.stats import linregress
root = Path('/root/work')
with (root / 'monthly_water_temperature.csv').open(newline='') as f:
    records = [(int(row['Year']), int(row['Month']), float(row['TempC'])) for row in csv.DictReader(f) if row['TempC'] != '']
monthly = {m: [v for _, month, v in records if month == m] for m in range(1, 13)}
means = {m: sum(values) / len(values) for m, values in monthly.items()}
seasons = []
for label, months in [('DJF', (12, 1, 2)), ('MAM', (3, 4, 5)), ('JJA', (6, 7, 8)), ('SON', (9, 10, 11))]:
    selected = [(y + (m - 0.5) / 12, v - means[m]) for y, m, v in records if m in months]
    fit = linregress([x for x, _ in selected], [a for _, a in selected])
    trend = 'warming' if fit.pvalue < 0.05 and fit.slope > 0 else ('cooling' if fit.pvalue < 0.05 and fit.slope < 0 else 'no_trend')
    seasons.append({'season': label, 'slope': round(float(fit.slope), 6), 'p_value': round(float(fit.pvalue), 6), 'trend': trend})
(root / 'seasonal_trends.json').write_text(json.dumps({'unit': 'C_per_year', 'seasons': seasons}, indent=2) + '\n')
PY
python /root/work/solve_seasons.py
