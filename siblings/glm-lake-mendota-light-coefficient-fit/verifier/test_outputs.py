import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

ROOT = Path('/root/work')
SRC = ROOT / 'glm3.nml'
OUT = ROOT / 'calibrated_glm3.nml'
PAT = r'(?im)^(\s*Kw\s*=\s*)([0-9.eE+-]+)'

def expected():
    original = SRC.read_text()
    current = float(re.search(PAT, original).group(2))
    depth_limit = float(re.search(r'(?im)^\s*lake_depth\s*=\s*([0-9.]+)', original).group(1))
    with (ROOT / 'bcs/meteo.csv').open() as f:
        sunlight = {r['datetime']: float(r['shortwave_W_m2']) for r in csv.DictReader(f)}
    with netcdf_file(ROOT / 'output/output.nc', 'r', mmap=False) as nc:
        hours = np.array(nc.variables['time'][:])
        heights = np.array(nc.variables['z'][:])[:, :, 0, 0]
        temps = np.array(nc.variables['temp'][:])[:, :, 0, 0]
    lookup = {}
    for i, hour in enumerate(hours):
        stamp = (datetime(2009, 1, 1, 12) + timedelta(hours=float(hour))).isoformat()
        for h, temp in zip(heights[i], temps[i]):
            lookup[stamp, round(depth_limit - h, 6)] = float(temp)
    xs, ys = [], []
    with (ROOT / 'field_temp_oxy.csv').open() as f:
        for row in csv.DictReader(f):
            stamp, d = row['datetime'], float(row['depth_m'])
            key = (stamp, round(d, 6))
            if key in lookup and stamp in sunlight:
                xs.append((d - 10) * sunlight[stamp] / 200)
                ys.append(float(row['temp_C']) - lookup[key])
    return current + sum(x*y for x, y in zip(xs, ys)) / sum(x*x for x in xs)

def test_file_exists():
    assert OUT.is_file()

def test_single_kw_and_four_decimals():
    matches = re.findall(PAT, OUT.read_text())
    assert len(matches) == 1
    assert re.fullmatch(r'[0-9]+\.[0-9]{4}', matches[0][1])

def test_other_namelist_content_unchanged():
    assert re.sub(PAT, r'\g<1>VALUE', OUT.read_text()) == re.sub(PAT, r'\g<1>VALUE', SRC.read_text())

def test_fitted_coefficient():
    actual = float(re.search(PAT, OUT.read_text()).group(2))
    assert abs(actual - expected()) <= 0.000051
