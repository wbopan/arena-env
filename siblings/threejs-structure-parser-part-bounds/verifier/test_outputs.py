import csv
import json
from pathlib import Path

INPUT = Path('/root/work/scene.json')
OUTPUT = Path('/root/work/part_bounds.csv')
HEADER = ['part', 'mesh_count', 'vertex_count', 'min_x', 'min_y', 'min_z', 'max_x', 'max_y', 'max_z', 'centroid_x', 'centroid_y', 'centroid_z']

def transform(m, point):
    v = (*point, 1)
    return tuple(sum(m[4*j+i] * v[j] for j in range(4)) for i in range(3))

def expected():
    grouped = {}
    def walk(node, ancestors, owner):
        chain = ancestors + [node['matrix']]
        if node['type'] == 'Group' and node.get('name'):
            owner = node['name']
            grouped[owner] = {'meshes': 0, 'points': []}
        if node['type'] == 'Mesh' and owner is not None:
            entry = grouped[owner]
            entry['meshes'] += 1
            values = node['positions']
            for start in range(0, len(values), 3):
                point = values[start:start+3]
                for m in reversed(chain):
                    point = transform(m, point)
                entry['points'].append(point)
        for child in node.get('children', []):
            walk(child, chain, owner)
    walk(json.loads(INPUT.read_text())['object'], [], None)
    return {name: item for name, item in grouped.items() if item['points']}

def table():
    with OUTPUT.open(newline='') as f:
        return list(csv.DictReader(f))

def test_file_exists():
    assert OUTPUT.is_file()

def test_header_and_part_order():
    with OUTPUT.open(newline='') as f:
        assert next(csv.reader(f)) == HEADER
    assert [row['part'] for row in table()] == sorted(expected())

def test_counts():
    for row in table():
        entry = expected()[row['part']]
        assert int(row['mesh_count']) == entry['meshes']
        assert int(row['vertex_count']) == len(entry['points'])

def test_bounds():
    for row in table():
        points = expected()[row['part']]['points']
        for axis, letter in enumerate('xyz'):
            assert abs(float(row['min_' + letter]) - min(p[axis] for p in points)) <= 0.0000006
            assert abs(float(row['max_' + letter]) - max(p[axis] for p in points)) <= 0.0000006

def test_centroids_and_precision():
    for row in table():
        points = expected()[row['part']]['points']
        for axis, letter in enumerate('xyz'):
            key = 'centroid_' + letter
            assert abs(float(row[key]) - sum(p[axis] for p in points) / len(points)) <= 0.0000006
        for key in HEADER[3:]:
            assert len(row[key].split('.')[-1]) == 6 and '.' in row[key]
