import csv
import json
from pathlib import Path
from scipy import stats

ROOT = Path('/root/work')
ORDER = ['DJF', 'MAM', 'JJA', 'SON']

def expected():
    with (ROOT / 'monthly_water_temperature.csv').open(newline='') as f:
        observations = [(int(r['Year']), int(r['Month']), float(r['TempC'])) for r in csv.DictReader(f) if r['TempC'] != '']
    means = {m: sum(v for _, month, v in observations if month == m) / sum(month == m for _, month, _ in observations) for m in range(1, 13)}
    result = {}
    for season, months in zip(ORDER, [(12, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11)]):
        points = [(year + (month - 0.5) / 12, value - means[month]) for year, month, value in observations if month in months]
        fit = stats.linregress([p[0] for p in points], [p[1] for p in points])
        label = 'warming' if fit.pvalue < 0.05 and fit.slope > 0 else ('cooling' if fit.pvalue < 0.05 and fit.slope < 0 else 'no_trend')
        result[season] = (fit.slope, fit.pvalue, label)
    return result

def output():
    return json.loads((ROOT / 'seasonal_trends.json').read_text())

def test_file_exists():
    assert (ROOT / 'seasonal_trends.json').is_file()

def test_schema_and_order():
    data = output()
    assert set(data) == {'unit', 'seasons'}
    assert data['unit'] == 'C_per_year'
    assert [row['season'] for row in data['seasons']] == ORDER
    assert all(set(row) == {'season', 'slope', 'p_value', 'trend'} for row in data['seasons'])

def test_slopes():
    reference = expected()
    assert all(abs(row['slope'] - reference[row['season']][0]) <= 0.000001 for row in output()['seasons'])

def test_p_values():
    reference = expected()
    assert all(abs(row['p_value'] - reference[row['season']][1]) <= 0.000001 and 0 <= row['p_value'] <= 1 for row in output()['seasons'])

def test_trend_labels():
    reference = expected()
    assert all(row['trend'] == reference[row['season']][2] for row in output()['seasons'])
