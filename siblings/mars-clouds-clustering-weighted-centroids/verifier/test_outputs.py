import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path('/root/work')
FIELDS = ['file_rad', 'cluster_id', 'n_points', 'centroid_x', 'centroid_y']


def expected():
    groups = defaultdict(list)
    with (ROOT / 'citsci.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            groups[row['file_rad']].append((float(row['x']), float(row['y'])))
    result = []
    for image in sorted(groups):
        points = groups[image]
        neighbors = []
        for x, y in points:
            neighbors.append([j for j, (u, v) in enumerate(points) if math.hypot(1.5 * (x-u), 0.5 * (y-v)) <= 2.5])
        core = {i for i, adj in enumerate(neighbors) if len(adj) >= 3}
        labels = [-1] * len(points)
        cluster = 0
        for start in range(len(points)):
            if start not in core or labels[start] != -1:
                continue
            queue = [start]
            labels[start] = cluster
            for i in queue:
                for j in neighbors[i]:
                    if labels[j] == -1:
                        labels[j] = cluster
                        if j in core:
                            queue.append(j)
            cluster += 1
        for cid in range(cluster):
            members = [points[i] for i, label in enumerate(labels) if label == cid]
            result.append((image, cid, len(members), sum(x for x, _ in members)/len(members), sum(y for _, y in members)/len(members)))
    return result


def read_output():
    with (ROOT / 'centroids.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == FIELDS
        return list(reader)


def test_exists():
    assert (ROOT / 'centroids.csv').is_file()


def test_schema_and_order():
    rows = read_output()
    assert rows
    keys = [(r['file_rad'], int(r['cluster_id'])) for r in rows]
    assert keys == sorted(keys)
    assert len(keys) == len(set(keys))


def test_cluster_counts():
    actual = read_output()
    want = expected()
    assert [(r['file_rad'], int(r['cluster_id']), int(r['n_points'])) for r in actual] == [(a, b, c) for a, b, c, _, _ in want]


def test_centroid_coordinates():
    actual = read_output()
    want = expected()
    assert len(actual) == len(want)
    for row, (_, _, _, x, y) in zip(actual, want):
        assert abs(float(row['centroid_x']) - x) <= 0.000051
        assert abs(float(row['centroid_y']) - y) <= 0.000051
