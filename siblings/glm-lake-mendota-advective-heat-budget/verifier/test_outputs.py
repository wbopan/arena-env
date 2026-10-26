import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from scipy.io import netcdf_file

ROOT = Path('/root/work')
OUT = ROOT / 'advective_budget.csv'
HEADER = ['date', 'inflow_m3', 'outflow_m3', 'net_heat_MJ']

def source_paths():
    text = (ROOT / 'glm3.nml').read_text()
    inflow = re.search(r'(?is)inflow_fl\s*=\s*([^\n]+)', text).group(1)
    outflow = re.search(r'(?is)outflow_fl\s*=\s*([^\n]+)', text).group(1)
    return re.findall(r"'([^']+)'", inflow), re.findall(r"'([^']+)'", outflow)[0]

def expected():
    incoming_paths, outgoing_path = source_paths()
    with (ROOT / outgoing_path).open() as f:
        withdrawals = {r['date']: float(r['flow_m3_s']) for r in csv.DictReader(f)}
    with netcdf_file(ROOT / 'output/output.nc', 'r', mmap=False) as nc:
        hours = np.array(nc.variables['time'][:])
        heights = np.array(nc.variables['z'][:])[:, :, 0, 0]
        temps = np.array(nc.variables['temp'][:])[:, :, 0, 0]
    surface = {}
    for i, hour in enumerate(hours):
        date = (datetime(2009, 1, 1, 12) + timedelta(hours=float(hour))).date().isoformat()
        surface[date] = float(temps[i, int(np.argmax(heights[i]))])
    contributions = {date: [] for date in withdrawals}
    for path in incoming_paths:
        with (ROOT / path).open() as f:
            for row in csv.DictReader(f):
                contributions[row['date']].append((float(row['flow_m3_s']), float(row['temp_C'])))
    answer = {}
    for date in withdrawals:
        flows = contributions[date]
        in_volume = 86400 * sum(q for q, _ in flows)
        out_volume = 86400 * withdrawals[date]
        heat = 4.186 * (86400 * sum(q*t for q, t in flows) - out_volume * surface[date])
        answer[date] = (in_volume, out_volume, heat)
    return answer

def test_file_exists():
    assert OUT.is_file()

def test_header_and_dates():
    with OUT.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert reader.fieldnames == HEADER
    assert [r['date'] for r in rows] == sorted(expected())

def test_numeric_format():
    with OUT.open() as f:
        for row in csv.DictReader(f):
            for column in HEADER[1:]:
                assert re.fullmatch(r'-?\d+\.\d{3}', row[column])

def test_budget_values():
    with OUT.open() as f:
        for row in csv.DictReader(f):
            for actual, target in zip((float(row[c]) for c in HEADER[1:]), expected()[row['date']]):
                assert abs(actual - target) <= 0.00051
