import json
import random

random.seed(2024)

PAGES = ['/', '/compare', '/products', '/cart', '/checkout', '/search', '/account', '/deals']

rows = []
for page in PAGES:
    t = random.uniform(100, 800)
    n = random.randint(6, 18)
    for i in range(n):
        if i > 0:
            if random.random() < 0.7:
                t += random.uniform(20, 700)
            else:
                t += random.uniform(1000, 3000)
        rows.append({
            'page': page,
            'startTime': round(t, 1),
            'value': round(random.uniform(0.002, 0.09), 4),
            'hadRecentInput': bool(i > 0 and random.random() < 0.15),
        })

random.shuffle(rows)
with open('layout_shifts.jsonl', 'w') as f:
    for r in rows:
        f.write(json.dumps(r) + '\n')
