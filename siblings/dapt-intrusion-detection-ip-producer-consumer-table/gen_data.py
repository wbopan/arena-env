import csv
import random

random.seed(34191)
ips = [f'10.18.0.{i}' for i in range(1, 9)]
rows = []
for i in range(105):
    src = random.choice(ips[:5] if i % 3 else ips)
    dst = random.choice(ips[3:])
    if src == dst:
        dst = ips[(ips.index(dst) + 1) % len(ips)]
    proto = random.choice(['TCP', 'UDP', 'ICMP'])
    sport = random.randint(1024, 60000) if proto != 'ICMP' else ''
    dport = random.choice([53, 80, 443, 8080]) if proto != 'ICMP' else ''
    rows.append([f'{1700000000 + i * 0.37:.2f}', src, dst, sport, dport, proto, random.randint(55, 1400)])
for i in range(5):
    rows.append([str(1700000002 + i), '', '', '', '', 'ARP', 42])
random.shuffle(rows)
with open('traffic.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ts', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'proto', 'length'])
    w.writerows(rows)
