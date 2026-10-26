import csv
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

ROOT = Path('/root/work')
OUT = ROOT / 'heat_storage.json'

def expected():
    config = (ROOT / 'glm3.nml').read_text()
    lake_depth = float(re.search(r'(?im)^\s*lake_depth\s*=\s*([\d.]+)', config).group(1))
    with (ROOT / 'bcs/hypsography.csv').open() as f:
        geometry = sorted((float(r['height_m']), float(r['area_m2'])) for r in csv.DictReader(f))
    levels, areas = map(np.array, zip(*geometry))
    with netcdf_file(ROOT / 'output/output.nc', 'r', mmap=False) as nc:
        hours = np.array(nc.variables['time'][:])
        centres = np.array(nc.variables['z'][:])[:, :, 0, 0]
        temperatures = np.array(nc.variables['temp'][:])[:, :, 0, 0]
    result = []
    previous = None
    for i, hour in enumerate(hours):
        order = np.argsort(centres[i])
        h, t = centres[i, order], temperatures[i, order]
        edges = np.r_[0., (h[:-1] + h[1:]) / 2., lake_depth]
        edge_areas = np.interp(edges, levels, areas)
        volumes = np.diff(edges) * (edge_areas[:-1] + edge_areas[1:]) / 2
        heat = float(np.sum(volumes * t) * 4.186 / 1000)
        date = (datetime(2009, 1, 1, 12) + timedelta(hours=float(hour))).isoformat()
        result.append((date, heat, 0. if previous is None else heat - previous))
        previous = heat
    return result

def test_file_exists():
    assert OUT.is_file()

def test_json_schema_and_count():
    rows = json.loads(OUT.read_text())
    assert isinstance(rows, list) and len(rows) == len(expected())
    assert all(isinstance(r, dict) and set(r) == {'datetime', 'heat_GJ', 'delta_GJ'} for r in rows)
    assert all(isinstance(r['heat_GJ'], (int, float)) and isinstance(r['delta_GJ'], (int, float)) for r in rows)

def test_datetimes():
    rows = json.loads(OUT.read_text())
    assert [r['datetime'] for r in rows] == [date for date, _, _ in expected()]

def test_heat_values():
    for row, (_, heat, _) in zip(json.loads(OUT.read_text()), expected()):
        assert abs(row['heat_GJ'] - heat) <= 0.00051

def test_deltas_use_unrounded_heats():
    for row, (_, _, change) in zip(json.loads(OUT.read_text()), expected()):
        assert abs(row['delta_GJ'] - change) <= 0.00051
