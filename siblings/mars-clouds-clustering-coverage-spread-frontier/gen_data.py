import csv
import random

random.seed(762)
rows = []
for image, shift in (('mesa', 0), ('dune', 29), ('plain', -18)):
    for cx, cy, count in ((14 + shift, 17, 7), (49 + shift, 43, 6)):
        for _ in range(count):
            rows.append((image, round(cx + random.uniform(-2.8, 2.8), 3), round(cy + random.uniform(-2.8, 2.8), 3)))
    for x, y in ((84 + shift, 5), (91 + shift, 72)):
        rows.append((image, x, y))
with open('citsci.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(('file_rad', 'x', 'y'))
    writer.writerows(rows)
