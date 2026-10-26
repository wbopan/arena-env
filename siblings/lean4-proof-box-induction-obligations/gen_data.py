import json
import random

random.seed(41027)
rows = []
for i in range(12):
    xmin = random.randint(-5, 0)
    xmax = random.randint(1, 6)
    ymin = random.randint(-5, 0)
    ymax = random.randint(1, 6)
    rows.append({
        'id': f'R{i:02d}',
        'start': [random.randint(-6, 7), random.randint(-6, 7)],
        'box': [xmin, xmax, ymin, ymax],
        'a': random.randint(-1, 1), 'b': random.randint(-1, 1),
        'c': random.randint(-3, 3), 'd': random.randint(-1, 1),
        'e': random.randint(-1, 1), 'f': random.randint(-3, 3),
    })
with open('recurrences.json', 'w', encoding='utf-8') as out:
    json.dump(rows, out, indent=2)
