import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path('/root/work')


def load(name, id_field):
    groups = defaultdict(list)
    with (ROOT / name).open(newline='') as f:
        for row in csv.DictReader(f):
            groups[row['file_rad']].append((int(row[id_field]), float(row['x']), float(row['y'])))
    return groups


def expected():
    clouds = load('centroids.csv', 'cluster_id')
    experts = load('expert.csv', 'expert_id')
    result = []
    for image in sorted(clouds.keys() | experts.keys()):
        candidates = []
        for c, x, y in clouds[image]:
            for e, u, v in experts[image]:
                d = math.sqrt((x-u)**2 + (y-v)**2)
                if d <= 16:
                    candidates.append((d, c, e))
        candidates.sort()
        used_c, used_e, matches = set(), set(), []
        for d, c, e in candidates:
            if c not in used_c and e not in used_e:
                matches.append({'cluster_id': c, 'expert_id': e, 'distance_px': round(d, 3)})
                used_c.add(c)
                used_e.add(e)
        result.append({'file_rad': image, 'matches': matches, 'unmatched_clusters': sorted(c for c, _, _ in clouds[image] if c not in used_c), 'unmatched_experts': sorted(e for e, _, _ in experts[image] if e not in used_e)})
    return result


def output():
    return json.loads((ROOT / 'matches.json').read_text())


def test_exists():
    assert (ROOT / 'matches.json').is_file()


def test_structure():
    data = output()
    assert set(data) == {'images'}
    assert isinstance(data['images'], list)
    for item in data['images']:
        assert set(item) == {'file_rad', 'matches', 'unmatched_clusters', 'unmatched_experts'}
        assert all(set(m) == {'cluster_id', 'expert_id', 'distance_px'} for m in item['matches'])


def test_images_and_unmatched():
    got, want = output()['images'], expected()
    assert [i['file_rad'] for i in got] == [i['file_rad'] for i in want]
    for a, b in zip(got, want):
        assert a['unmatched_clusters'] == b['unmatched_clusters']
        assert a['unmatched_experts'] == b['unmatched_experts']


def test_greedy_matches():
    got, want = output()['images'], expected()
    for a, b in zip(got, want):
        assert len(a['matches']) == len(b['matches'])
        for x, y in zip(a['matches'], b['matches']):
            assert (x['cluster_id'], x['expert_id']) == (y['cluster_id'], y['expert_id'])
            assert abs(x['distance_px'] - y['distance_px']) <= 0.00051
