#!/bin/bash
set -e
cat > /tmp/solve_wave_picks.py <<'PY'
import csv
from collections import defaultdict
from pathlib import Path

root = Path('/root/work')
with (root / 'stations.csv').open() as f:
    responses = {r['station_id']: float(r['response']) for r in csv.DictReader(f)}
traces = defaultdict(list)
with (root / 'waveforms.csv').open() as f:
    for r in csv.DictReader(f):
        traces[(r['station_id'], r['channel'])].append((int(r['sample']), abs(float(r['counts'])) / responses[r['station_id']]))
picks = []
for (station, channel), samples in traces.items():
    samples.sort()
    run = []
    for sample, amplitude in samples + [(10**9, 0)]:
        if run and (amplitude < 3 or sample != run[-1][0] + 1):
            if len(run) >= 2:
                picks.append((station, 'p' if channel == 'Z' else 's', run[0][0], max(a for _, a in run)))
            run = []
        if amplitude >= 3:
            run.append((sample, amplitude))
picks.sort(key=lambda r: (r[2], r[0], r[1]))
with (root / 'picks.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['station_id', 'phase', 'time_s', 'peak_unit'])
    for sid, phase, time, peak in picks:
        w.writerow([sid, phase, time, f'{peak:.2f}'])
PY
python /tmp/solve_wave_picks.py
