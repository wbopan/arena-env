#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json, re
body = []
for line in open('ci_log.txt').read().splitlines():
    p = line.split(' ', 1)
    body.append(p[1] if len(p) > 1 else '')
start = next(i for i, s in enumerate(body) if 'short test summary info' in s)
ents = []
for s in body[start + 1:]:
    if s.startswith('='):
        break
    if s.startswith('FAILED ') or s.startswith('ERROR '):
        kind, rest = s.split(' ', 1)
        nodeid, exc = rest.split(' - ', 1)
        ents.append((kind, nodeid, exc))
by, mods, files = {}, set(), {}
for kind, nodeid, exc in ents:
    et = exc.split(':', 1)[0].strip()
    by[et] = by.get(et, 0) + 1
    if et == 'ModuleNotFoundError':
        m = re.search(r"No module named '([^']+)'", exc)
        if m:
            mods.add(m.group(1).split('.')[0])
    f = nodeid.split('::', 1)[0]
    files[f] = files.get(f, 0) + 1
worst = sorted(files.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
out = {'failed': sum(e[0] == 'FAILED' for e in ents),
       'errors': sum(e[0] == 'ERROR' for e in ents),
       'by_exception': by, 'missing_modules': sorted(mods), 'worst_file': worst}
json.dump(out, open('ci_summary.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
