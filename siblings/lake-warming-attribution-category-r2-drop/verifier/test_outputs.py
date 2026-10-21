import csv
import os

import numpy as np
import pandas as pd
import pytest

D = '/root/work/'
OUT = D + 'contributions.csv'
CATS = {
    'Heat': ['AirTemp', 'NetRadiation', 'Humidity'],
    'Flow': ['Precip', 'Inflow', 'Outflow'],
    'Wind': ['WindSpeed'],
    'Human': ['DevelopedArea', 'AgricultureArea'],
}


def r2(df, cols):
    y = df['WaterTemp'].to_numpy(float)
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in cols])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    return 1 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)


def expected():
    df = pd.read_csv(D + 'water_temperature.csv')
    for f in ['climate.csv', 'hydrology.csv', 'land_cover.csv']:
        df = df.merge(pd.read_csv(D + f), on='Year', how='inner')
    df['NetRadiation'] = df['Shortwave'] + df['Longwave']
    allv = [v for vs in CATS.values() for v in vs]
    full = r2(df, allv)
    return {c: (full - r2(df, [v for v in allv if v not in vs])) * 100 for c, vs in CATS.items()}


@pytest.fixture(scope='module')
def rows():
    assert os.path.exists(OUT), 'contributions.csv not found'
    with open(OUT, newline='') as f:
        rd = csv.DictReader(f)
        assert rd.fieldnames is not None
        assert [h.strip() for h in rd.fieldnames] == ['category', 'contribution']
        return [{k.strip(): v.strip() for k, v in r.items()} for r in rd]


def test_schema(rows):
    assert len(rows) == 4
    assert sorted(r['category'] for r in rows) == sorted(CATS.keys())


def test_sorted_desc(rows):
    vals = [float(r['contribution']) for r in rows]
    assert vals == sorted(vals, reverse=True)


def test_values(rows):
    exp = expected()
    for r in rows:
        assert abs(float(r['contribution']) - exp[r['category']]) <= 0.02, r


def test_dominant(rows):
    exp = expected()
    assert rows[0]['category'] == max(exp, key=exp.get)
