import csv
import json
import math
from collections import defaultdict
from itertools import product
from pathlib import Path

ROOT = Path('/root/work')
FIELDS = {'epsilon', 'min_samples', 'shape_weight', 'coverage', 'spread_px'}


def inputs():
    groups = defaultdict(list)
    with (ROOT / 'citsci.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            groups[r['file_rad']].append((float(r['x']), float(r['y'])))
    return groups


def score(groups, eps, minimum, weight):
    assigned, spread, total = 0, 0.0, sum(map(len, groups.values()))
    for points in groups.values():
        near = [[j for j, (u, v) in enumerate(points) if math.sqrt((weight*(x-u))**2 + ((2-weight)*(y-v))**2) <= eps] for x, y in points]
        core = {i for i, adj in enumerate(near) if len(adj) >= minimum}
        labels = [-1] * len(points)
        cid = 0
        for seed in range(len(points)):
            if seed not in core or labels[seed] >= 0:
                continue
            frontier = [seed]
            labels[seed] = cid
            for i in frontier:
                for j in near[i]:
                    if labels[j] == -1:
                        labels[j] = cid
                        if j in core:
                            frontier.append(j)
            cid += 1
        for cluster in range(cid):
            members = [points[i] for i in range(len(points)) if labels[i] == cluster]
            assigned += len(members)
            mx = sum(p[0] for p in members)/len(members)
            my = sum(p[1] for p in members)/len(members)
            spread += sum(math.hypot(x-mx, y-my) for x, y in members)
    return assigned/total, spread/assigned if assigned else float('inf')


def expected():
    groups = inputs()
    candidates = []
    for eps, minimum, weight in product((2, 3, 4), (2, 3), (0.7, 1.0, 1.3)):
        coverage, spread = score(groups, eps, minimum, weight)
        if coverage >= 0.4:
            candidates.append((eps, minimum, weight, coverage, spread))
    return [p for p in candidates if not any(q[3] >= p[3] and q[4] <= p[4] and (q[3] > p[3] or q[4] < p[4]) for q in candidates)]


def output():
    return json.loads((ROOT / 'frontier.json').read_text())


def test_exists():
    assert (ROOT / 'frontier.json').is_file()


def test_schema_and_order():
    rows = output()
    assert isinstance(rows, list) and rows
    assert all(set(row) == FIELDS for row in rows)
    keys = [(r['epsilon'], r['min_samples'], r['shape_weight']) for r in rows]
    assert keys == sorted(set(keys))


def test_frontier_membership():
    rows, want = output(), expected()
    assert [(r['epsilon'], r['min_samples'], r['shape_weight']) for r in rows] == [(e, m, w) for e, m, w, _, _ in want]


def test_objectives():
    rows, want = output(), expected()
    assert len(rows) == len(want)
    for row, (_, _, _, coverage, spread) in zip(rows, want):
        assert abs(row['coverage'] - coverage) <= 0.0000051
        assert abs(row['spread_px'] - spread) <= 0.0000051
