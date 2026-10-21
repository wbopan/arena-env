#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_nearest.py <<'EOF'
import json
import xml.etree.ElementTree as ET
from collections import deque
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}
repo = json.load(open('repository.json'))
root = ET.parse('pom.xml').getroot()
q = deque()
for d in root.findall('m:dependencies/m:dependency', NS):
    ga = d.find('m:groupId', NS).text.strip() + ':' + d.find('m:artifactId', NS).text.strip()
    q.append((ga, d.find('m:version', NS).text.strip(), 1))
res = {}
while q:
    ga, v, depth = q.popleft()
    if ga in res:
        continue
    res[ga] = (v, depth)
    for e in repo[ga + ':' + v]:
        if not e['optional']:
            g, a, vv = e['coord'].split(':')
            q.append((g + ':' + a, vv, depth + 1))
with open('resolved.txt', 'w') as f:
    for ga in sorted(res):
        f.write('%s:%s %d\n' % (ga, res[ga][0], res[ga][1]))
EOF
python3 /tmp/solve_nearest.py
