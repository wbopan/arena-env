import csv
import json
import random

random.seed(4242)
rel = {}


def add(p, c):
    rel[(p, c)] = 'customer'
    rel[(c, p)] = 'provider'


def peer(a, b):
    rel[(a, b)] = 'peer'
    rel[(b, a)] = 'peer'


t1 = list(range(65001, 65005))
t2 = list(range(65010, 65022))
t3 = list(range(65100, 65130))
for i in range(len(t1)):
    for j in range(i + 1, len(t1)):
        peer(t1[i], t1[j])
for a in t2:
    for p in random.sample(t1, random.choice([1, 2])):
        add(p, a)


def add_peers(group, n):
    k = 0
    while k < n:
        a, b = random.sample(group, 2)
        if (a, b) in rel:
            continue
        peer(a, b)
        k += 1


add_peers(t2, 8)
for a in t3:
    for p in random.sample(t2, random.choice([1, 2])):
        add(p, a)
add_peers(t3, 6)
rows = []
seen = set()
for (a, b) in sorted(rel):
    key = (min(a, b), max(a, b))
    if key in seen:
        continue
    seen.add(key)
    if random.random() < 0.5:
        a, b = b, a
    rows.append((a, b, rel[(a, b)]))
random.shuffle(rows)
with open('relationships.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['as_a', 'as_b', 'relationship'])
    w.writerows(rows)
nbr = {}
for (a, b) in rel:
    nbr.setdefault(a, []).append(b)
for a in nbr:
    nbr[a].sort()
nodes = sorted(nbr)
props = []
pid = 1
while len(props) < 60:
    target = random.randint(3, 7)
    path = [random.choice(nodes)]
    while len(path) < target:
        opts = [x for x in nbr[path[-1]] if x not in path]
        if not opts:
            break
        path.append(random.choice(opts))
    if len(path) < 3:
        continue
    props.append({'path_id': pid, 'prefix': '10.%d.%d.0/24' % (pid // 256, pid % 256), 'as_path': path})
    pid += 1
with open('propagations.json', 'w') as f:
    json.dump(props, f, indent=1)
