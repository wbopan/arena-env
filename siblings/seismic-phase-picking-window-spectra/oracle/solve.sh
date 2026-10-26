#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_spectra.py <<'PY'
import csv
from pathlib import Path
import numpy as np
from openpyxl import Workbook

root = Path('/root/work')
windows = {}
with (root / 'windows.csv').open(newline='') as f:
    for row in csv.DictReader(f):
        windows[(row['file_name'], row['phase'])] = slice(int(row['start_idx']), int(row['end_idx']))
book = Workbook()
sheet = book.active
sheet.title = 'Spectra'
sheet.append(['file_name', 'p_high_fraction', 's_high_fraction', 's_hv_ratio'])
for path in sorted(root.glob('station_*.npz')):
    with np.load(path) as record:
        data = record['data']
        channels = str(record['channels']).split(',')
        dt = float(record['dt'])
    vertical = next(j for j, name in enumerate(channels) if name.endswith('Z'))
    horizontals = [j for j, name in enumerate(channels) if name.endswith(('E', 'N'))]
    p = data[windows[(path.name, 'P')]]
    s = data[windows[(path.name, 'S')]]
    vertical_power = np.abs(np.fft.rfft(p[:, vertical])) ** 2
    horizontal_power = sum(np.abs(np.fft.rfft(s[:, j])) ** 2 for j in horizontals)
    p_mask = np.fft.rfftfreq(len(p), dt) >= 8
    s_mask = np.fft.rfftfreq(len(s), dt) >= 8
    p_fraction = vertical_power[p_mask].sum() / vertical_power.sum()
    s_fraction = horizontal_power[s_mask].sum() / horizontal_power.sum()
    hv = np.sum(s[:, horizontals].astype('float64') ** 2) / np.sum(s[:, vertical].astype('float64') ** 2)
    sheet.append([path.name, round(float(p_fraction), 4), round(float(s_fraction), 4), round(float(hv), 4)])
book.save(root / 'spectra.xlsx')
PY
python /tmp/solve_spectra.py
