import csv
import json
from pathlib import Path
import numpy as np

ROOT = Path('/root/work')
NAMES = ['AirTemp', 'Radiation', 'WindSpeed', 'Inflow', 'Runoff', 'DevelopedPct', 'AgriculturePct', 'TreeCoverPct']
GROUPS = {'Heat': NAMES[:2], 'Flow': NAMES[3:5], 'Wind': NAMES[2:3], 'Human': NAMES[5:]}

def expected():
    by_year = {}
    for file in ['climate.csv', 'hydrology.csv', 'land_cover.csv']:
        with (ROOT / file).open(newline='') as f:
            for row in csv.DictReader(f):
                by_year.setdefault(int(row['Year']), {}).update(row)
    matrix = np.array([[float(by_year[y][name]) for name in NAMES] for y in sorted(by_year)])
    centered = matrix - matrix.mean(axis=0)
    standardized = centered / np.sqrt(np.mean(centered ** 2, axis=0))
    eigenvalues, eigenvectors = np.linalg.eigh(standardized.T @ standardized / len(matrix))
    order = np.argsort(eigenvalues)[::-1]
    vals = eigenvalues[order]
    vector = eigenvectors[:, order[0]]
    if vector[np.argmax(np.abs(vector))] < 0:
        vector = -vector
    shares = {group: 100 * sum(vector[NAMES.index(name)] ** 2 for name in members) for group, members in GROUPS.items()}
    return vals, vector, shares

def output():
    return json.loads((ROOT / 'pca_summary.json').read_text())

def test_file_exists():
    assert (ROOT / 'pca_summary.json').is_file()

def test_schema():
    data = output()
    assert set(data) == {'pc1_variance_pct', 'pc2_variance_pct', 'pc1_loadings', 'dominant_category', 'category_share_pct'}
    assert set(data['pc1_loadings']) == set(NAMES)

def test_variance():
    vals, _, _ = expected()
    data = output()
    assert abs(data['pc1_variance_pct'] - 100 * vals[0] / sum(vals)) <= 0.000001
    assert abs(data['pc2_variance_pct'] - 100 * vals[1] / sum(vals)) <= 0.000001

def test_loadings():
    _, vector, _ = expected()
    assert all(abs(output()['pc1_loadings'][name] - vector[i]) <= 0.000001 for i, name in enumerate(NAMES))

def test_dominant_category():
    _, _, shares = expected()
    data = output()
    winner = max(shares, key=shares.get)
    assert data['dominant_category'] == winner
    assert abs(data['category_share_pct'] - shares[winner]) <= 0.000001
