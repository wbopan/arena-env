#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import csv, glob
import xml.etree.ElementTree as ET
stats = {}
for f in sorted(glob.glob('runs/*.xml')):
    for tc in ET.parse(f).getroot().iter('testcase'):
        tid = tc.get('classname') + '::' + tc.get('name')
        tags = {c.tag for c in tc}
        s = stats.setdefault(tid, [0, 0])
        if 'failure' in tags or 'error' in tags:
            s[0] += 1; s[1] += 1
        elif 'skipped' in tags:
            pass
        else:
            s[0] += 1
rows = []
for tid, (runs, fails) in stats.items():
    if runs == 0 or fails == 0:
        continue
    rows.append((tid, 'broken' if fails == runs else 'flaky', runs, fails, fails / runs))
rows.sort(key=lambda r: (0 if r[1] == 'broken' else 1, -r[4], r[0]))
with open('flaky_report.csv', 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['test_id', 'status', 'runs', 'failures', 'fail_rate'])
    for r in rows:
        w.writerow([r[0], r[1], r[2], r[3], f'{r[4]:.3f}'])
EOF
python3 /tmp/solve.py
