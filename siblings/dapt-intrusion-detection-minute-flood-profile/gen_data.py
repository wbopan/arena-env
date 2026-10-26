import csv
import random

random.seed(73015)
base = 1710000000
rows = []
for minute in range(29):
    count = random.randint(1, 4) if minute != 17 else random.randint(440, 520)
    for j in range(count):
        ts = base + 60 * minute + random.randint(0, 58000) / 1000
        proto = random.choice(['TCP', 'UDP', 'ARP'])
        ip = proto != 'ARP'
        rows.append([f'{ts:.3f}', '192.0.2.10' if ip else '', '198.51.100.20' if ip else '',
                     41000 if ip else '', 443 if ip else '', proto, random.randint(42, 900)])
random.shuffle(rows)
with open('traffic.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ts', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'proto', 'length'])
    w.writerows(rows)
