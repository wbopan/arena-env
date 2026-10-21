#!/bin/bash
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json, csv
d = json.load(open('shifts.json'))
with open('cls_report.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['url', 'cls', 'rating', 'windows', 'max_window_start_ms'])
    for p in d['pages']:
        es = sorted([e for e in p['entries'] if not e['hadRecentInput']], key=lambda e: e['startTime'])
        wins = []
        last = None
        for e in es:
            t = e['startTime']
            if not wins or t - last > 1000 or t - wins[-1][0] > 5000:
                wins.append([t, 0.0])
            wins[-1][1] += e['value']
            last = t
        if wins:
            best = max(x[1] for x in wins)
            start = next(x[0] for x in wins if x[1] == best)
        else:
            best, start = 0.0, ''
        rating = 'good' if best < 0.1 else ('needs-improvement' if best <= 0.25 else 'poor')
        w.writerow([p['url'], f'{best:.4f}', rating, len(wins), start])
EOF
python3 /tmp/solve.py
