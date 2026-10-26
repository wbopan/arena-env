#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_minute_profile.py <<'PY'
import csv
import json
from collections import Counter
from math import floor

with open('/root/work/traffic.csv', newline='') as f:
    times = [float(row['ts']) for row in csv.DictReader(f)]
origin = min(times)
minutes = Counter(floor((t-origin)/60) for t in times)
total = len(times)
average = total / len(minutes)
peak = max(minutes.values())
report = {
    'total_packets': total,
    'occupied_minutes': len(minutes),
    'average_ppm': round(average, 3),
    'peak_ppm': peak,
    'has_dos_pattern': peak / average > 20,
    'buckets': [
        {'minute_index': m, 'packet_count': minutes[m],
         'share_percent': round(100 * minutes[m] / total, 3)}
        for m in sorted(minutes)
    ],
}
with open('/root/work/minute_profile.json', 'w') as f:
    json.dump(report, f, indent=2)
PY
python3 /tmp/solve_minute_profile.py
