#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_http_audit.py <<'PY'
import json
import re

answer = []
for line in open('requests.jsonl'):
    record = json.loads(line)
    header, body = record['request'].split('\r\n\r\n', 1)
    first, *header_lines = header.split('\r\n')
    words = first.split(' ')
    mode = [h.partition(':')[2].strip() for h in header_lines
            if h.partition(':')[0].lower() == 'x-tlm-mode']
    params = dict(chunk.split('=', 1) for chunk in body.split('&'))
    blob = params.get('blob', '')
    sig = params.get('sig', '')
    if (words[0] == 'POST' and words[1] == '/telemetry/v2/report'
            and 'exfil' in mode and re.fullmatch('[A-Za-z0-9+/=]{80,}', blob)
            and re.fullmatch('[0-9a-fA-F]{64}', sig)):
        answer.append(dict(id=record['id'], blob_chars=len(blob), sig_prefix=sig[:8]))
with open('qualified.json', 'w') as f:
    json.dump(sorted(answer, key=lambda r: r['id']), f)
PY
python /tmp/solve_http_audit.py
