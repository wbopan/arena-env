import json
import random
import string

random.seed(4107)
alphabet = string.ascii_letters + string.digits + '+/'
hexchars = '0123456789abcdefABCDEF'
rows = []
for i in range(24):
    kind = i % 8
    blob = ''.join(random.choices(alphabet, k=80 + i % 7))
    sig = ''.join(random.choices(hexchars, k=64))
    method = 'POST' if kind != 1 else 'GET'
    path = '/telemetry/v2/report' if kind != 2 else '/telemetry/v2/reporting'
    mode = 'exfil' if kind != 3 else 'normal'
    if kind == 4:
        blob = blob[:79]
    if kind == 5:
        blob = blob[:35] + '-' + blob[36:]
    if kind == 6:
        sig = sig[:-1]
    if kind == 7:
        sig = sig[:20] + 'Z' + sig[21:]
    body = f'blob={blob}&sig={sig}' if i % 2 else f'sig={sig}&blob={blob}'
    header = 'x-tlm-mode' if i % 3 else 'X-TLM-Mode'
    request = (f'{method} {path} HTTP/1.1\r\nHost: collector.test\r\n'
               f'{header}: {mode}\r\nContent-Length: {len(body)}\r\n\r\n{body}')
    rows.append({'id': 800 + i, 'request': request})
random.shuffle(rows)
with open('requests.jsonl', 'w') as out:
    for row in rows:
        out.write(json.dumps(row) + '\n')
