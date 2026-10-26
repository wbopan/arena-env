#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_eve.py <<'PY'
import csv
import ipaddress
import json
from collections import defaultdict

requests = {}
alerts = set()
for line in open('eve.json'):
    event = json.loads(line)
    key = (event.get('flow_id'), event.get('tx_id'))
    if event['event_type'] == 'http':
        requests[key] = event
    elif event['event_type'] == 'alert' and event['alert']['signature_id'] == 1000001:
        alerts.add(key)
counts = defaultdict(lambda: [0, 0])
for key, event in requests.items():
    h = event['http']
    if (key in alerts and h['http_method'] == 'POST'
            and h['url'] == '/telemetry/v2/report' and h['x_tlm_mode'] == 'exfil'):
        counts[event['src_ip']][0] += 1
        counts[event['src_ip']][1] += h['request_body_len']
with open('source_totals.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['src_ip', 'transactions', 'body_bytes'])
    for ip in sorted(counts, key=ipaddress.ip_address):
        writer.writerow([ip, *counts[ip]])
PY
python /tmp/solve_eve.py
