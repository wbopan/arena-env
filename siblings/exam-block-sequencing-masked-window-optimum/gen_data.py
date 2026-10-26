import csv
import itertools
import json
import random

random.seed(31841)
blocks = [f'B{i}' for i in range(7)]
slots = ['M1', 'M3', 'T2', 'W1', 'W4', 'F1', 'F3']
instance = {'slot_order': slots, 'blocks': blocks, 'large_blocks': ['B1', 'B5'], 'early_slots': slots[:3], 'pair_starts': [0, 1, 3, 4, 5], 'triple_starts': [0, 2, 3, 4]}
with open('instance.json', 'w') as f:
    json.dump(instance, f, indent=2)
for filename, length, columns, maximum in [('pair_counts.csv', 2, ['first', 'second', 'count'], 9), ('triple_counts.csv', 3, ['first', 'second', 'third', 'count'], 6)]:
    with open(filename, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(columns)
        for key in itertools.permutations(blocks, length):
            w.writerow([*key, random.randrange(maximum + 1)])
