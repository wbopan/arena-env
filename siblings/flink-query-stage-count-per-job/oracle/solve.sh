#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_stages.py <<'EOF'
import gzip

GAP = 600 * 10**6
finished = set()
for line in gzip.open('data/job_events.csv.gz', 'rt'):
    p = line.rstrip('\n').split(',')
    if len(p) > 3 and p[3] == '4':
        finished.add(int(p[2]))
subs = {}
for line in gzip.open('data/task_events.csv.gz', 'rt'):
    p = line.rstrip('\n').split(',')
    if len(p) > 5 and p[5] == '0':
        subs.setdefault(int(p[2]), []).append(int(p[0]))
out = ['job_id,num_stages,largest_stage']
for jid in sorted(subs):
    if jid not in finished:
        continue
    ts = sorted(subs[jid])
    stages = []
    prev = None
    for t in ts:
        if prev is None or t - prev >= GAP:
            stages.append(0)
        stages[-1] += 1
        prev = t
    out.append('%d,%d,%d' % (jid, len(stages), max(stages)))
open('stages.csv', 'w').write('\n'.join(out) + '\n')
EOF
python3 /tmp/solve_stages.py
