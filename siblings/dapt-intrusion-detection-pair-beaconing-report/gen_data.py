import csv
import random

random.seed(7331)

base = 1700000000.0
internal = ['10.20.0.%d' % i for i in random.sample(range(2, 200), 9)]
external = ['203.0.113.%d' % i for i in random.sample(range(2, 250), 6)] + ['198.51.100.%d' % i for i in random.sample(range(2, 250), 5)]
used = set()
rows = []


def pick():
    while True:
        p = (random.choice(internal), random.choice(external))
        if p not in used and (p[1], p[0]) not in used:
            used.add(p)
            return p


def emit(src, dst, times, proto, dport, lo, hi):
    sp = random.randint(49152, 65535)
    for t in times:
        rows.append(['%.3f' % (base + t), src, dst, sp, dport, proto, random.randint(lo, hi)])


def bursty(n):
    t = random.uniform(0, 300)
    out = []
    for _ in range(n):
        out.append(t)
        if random.random() < 0.7:
            t += random.expovariate(1 / 2.0)
        else:
            t += random.expovariate(1 / 150.0)
    return out


for _ in range(random.randint(1, 3)):
    s, d = pick()
    period = random.uniform(20, 90)
    n = random.randint(12, 22)
    start = random.uniform(0, 200)
    times = [start + k * period + random.uniform(-0.08, 0.08) * period for k in range(n)]
    emit(s, d, times, random.choice(['TCP', 'UDP']), random.choice([443, 8080, 53]), 60, 300)

normal = []
for _ in range(4):
    s, d = pick()
    normal.append((s, d))
    emit(s, d, bursty(random.randint(12, 22)), 'TCP', random.choice([80, 443, 22]), 60, 1500)

for s, d in random.sample(normal, 2):
    used.add((d, s))
    emit(d, s, bursty(random.randint(10, 15)), 'TCP', random.randint(49152, 65535), 60, 1500)

for _ in range(5):
    s, d = pick()
    emit(s, d, [random.uniform(0, 2000) for _ in range(random.randint(2, 8))], 'UDP', 53, 40, 120)

for _ in range(8):
    rows.append(['%.3f' % (base + random.uniform(0, 2000)), '', '', '', '', 'ARP', 42])

random.shuffle(rows)
with open('traffic.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ts', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'proto', 'length'])
    w.writerows(rows)
