import csv
import random

random.seed(413)
rows = []
experts = []
for image in ('crater_a', 'crater_b', 'ridge_c'):
    shift = {'crater_a': 0, 'crater_b': 7, 'ridge_c': -5}[image]
    for cx, cy, n in ((12 + shift, 15, 6), (48 + shift, 39, 5)):
        experts.append((image, cx, cy))
        for _ in range(n):
            rows.append((image, round(cx + random.uniform(-1.3, 1.3), 3), round(cy + random.uniform(-2.0, 2.0), 3)))
    rows.extend(((image, 86 + shift, 4), (image, 91 + shift, 70)))
for path, data in (('citsci.csv', rows), ('expert.csv', experts)):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('file_rad', 'x', 'y'))
        writer.writerows(data)
