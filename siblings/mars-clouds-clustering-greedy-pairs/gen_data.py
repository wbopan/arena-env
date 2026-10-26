import csv
import random

random.seed(109)
centroids = []
experts = []
for image, offset in (('north', 0), ('south', 50), ('west', 100)):
    for i, (x, y) in enumerate(((10, 10), (24, 10), (43, 28), (76, 62))):
        centroids.append((image, i, round(x + offset + random.uniform(-2, 2), 3), round(y + random.uniform(-2, 2), 3)))
    for i, (x, y) in enumerate(((17, 10), (10, 12), (44, 29), (92, 62))):
        experts.append((image, i, round(x + offset + random.uniform(-1, 1), 3), round(y + random.uniform(-1, 1), 3)))
experts.append(('empty_image', 0, 8, 8))
for name, header, rows in (('centroids.csv', ('file_rad', 'cluster_id', 'x', 'y'), centroids), ('expert.csv', ('file_rad', 'expert_id', 'x', 'y'), experts)):
    with open(name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
