import csv
import itertools
import json
import random

random.seed(94106)
blocks = [f'E{i}' for i in range(7)]
slots = ['MON-AM', 'MON-PM', 'TUE-AM', 'WED-AM', 'WED-PM', 'THU-AM', 'FRI-AM']
with open('instance.json', 'w') as f:
    json.dump({'slot_order': slots, 'blocks': blocks, 'large_blocks': ['E1', 'E4'], 'early_slots': slots[:3]}, f, indent=2)
for path, size, header, maximum in [('pair_counts.csv', 2, ['first', 'second', 'count'], 12), ('triple_counts.csv', 3, ['first', 'second', 'third', 'count'], 8)]:
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for tup in itertools.permutations(blocks, size):
            w.writerow([*tup, random.randrange(maximum + 1)])
