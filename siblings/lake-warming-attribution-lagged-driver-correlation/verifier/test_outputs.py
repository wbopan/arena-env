import csv
from pathlib import Path
import numpy as np

ROOT = Path('/root/work')
SOURCES = [('Heat', 'AirTemp', 'climate.csv'), ('Flow', 'Inflow', 'hydrology.csv'), ('Wind', 'WindSpeed', 'climate.csv'), ('Human', 'DevelopedPct', 'land_cover.csv')]
FIELDS = ['category', 'driver', 'lag_years', 'pearson_r', 'abs_r_pct']

def read_series(file, column):
    with (ROOT / file).open(newline='') as f:
        return {int(row['Year']): float(row[column]) for row in csv.DictReader(f)}

def expected():
    water = read_series('water_temperature.csv', 'WaterTemp')
    response = np.array([water[t] - water[t - 1] for t in range(2004, 2033)])
    result = []
    for category, driver, file in SOURCES:
        series = read_series(file, driver)
        correlations = []
        for lag in (0, 1, 2):
            changes = np.array([series[t - lag] - series[t - lag - 1] for t in range(2004, 2033)])
            correlations.append(float(np.corrcoef(response, changes)[0, 1]))
        best = max(range(3), key=lambda lag: abs(correlations[lag]))
        result.append((category, driver, best, correlations[best]))
    return result

def output():
    with (ROOT / 'lagged_associations.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def test_file_exists():
    assert (ROOT / 'lagged_associations.csv').is_file()

def test_schema_and_order():
    fields, rows = output()
    assert fields == FIELDS
    assert len(rows) == 4
    assert [(r['category'], r['driver']) for r in rows] == [(c, d) for c, d, _ in SOURCES]

def test_selected_lags():
    _, rows = output()
    assert [int(r['lag_years']) for r in rows] == [lag for _, _, lag, _ in expected()]

def test_signed_correlations():
    _, rows = output()
    assert all(abs(float(row['pearson_r']) - r) <= 0.000001 for row, (_, _, _, r) in zip(rows, expected()))

def test_absolute_percentages():
    _, rows = output()
    assert all(abs(float(row['abs_r_pct']) - 100 * abs(r)) <= 0.000001 for row, (_, _, _, r) in zip(rows, expected()))
