import json
import random

random.seed(9205)
events = []
sources = ['10.8.0.12', '10.8.0.3', '172.19.1.9', '192.0.2.15']
for i in range(32):
    flow, tx = 5000 + i // 2, i % 2
    src = sources[i % len(sources)]
    http = {'event_type': 'http', 'flow_id': flow, 'tx_id': tx, 'src_ip': src,
            'http': {'http_method': 'GET' if i % 11 == 0 else 'POST',
                     'url': '/telemetry/v2/reporting' if i % 9 == 0 else '/telemetry/v2/report',
                     'x_tlm_mode': 'normal' if i % 7 == 0 else 'exfil',
                     'request_body_len': random.randrange(78, 900)}}
    events.append(http)
    if i % 5 != 0:
        events.append({'event_type': 'alert', 'flow_id': flow, 'tx_id': tx,
                       'src_ip': '198.51.100.4',
                       'alert': {'signature_id': 2000002 if i % 6 == 0 else 1000001}})
        if i % 4 == 0:
            events.append({'event_type': 'alert', 'flow_id': flow, 'tx_id': tx,
                           'src_ip': '198.51.100.4', 'alert': {'signature_id': 1000001}})
events.append({'event_type': 'dns', 'flow_id': 9999, 'tx_id': 0})
random.shuffle(events)
with open('eve.json', 'w') as out:
    for event in events:
        out.write(json.dumps(event) + '\n')
