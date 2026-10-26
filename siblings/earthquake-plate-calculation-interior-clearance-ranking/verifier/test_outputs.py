import json
import math
from pathlib import Path

BASE = Path('/root/work')
R = 6378137 * math.pi / 180


def inside(p, ring):
    x, y = p
    flag = False
    for a, b in zip(ring, ring[1:]):
        ax, ay = a
        bx, by = b
        cross = (x-ax)*(by-ay)-(y-ay)*(bx-ax)
        if abs(cross) < 1e-10 and min(ax, bx) <= x <= max(ax, bx) and min(ay, by) <= y <= max(ay, by):
            return False
        if (ay > y) != (by > y) and x < ax + (y-ay)*(bx-ax)/(by-ay):
            flag = not flag
    return flag


def expected():
    plates = json.loads((BASE/'plates.geojson').read_text())['features']
    ring = next(f['geometry']['coordinates'][0] for f in plates if f['properties']['Code'] == 'PA')
    rows = []
    for q in json.loads((BASE/'earthquakes.json').read_text()):
        p = (q['longitude'], q['latitude'])
        if not inside(p, ring):
            continue
        distances = []
        for a, b in zip(ring, ring[1:]):
            dx, dy = b[0]-a[0], b[1]-a[1]
            t = max(0.0, min(1.0, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
            distances.append(R*math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy)/1000)
        rows.append((q['id'], min(distances)))
    return sorted(rows, key=lambda row: (-row[1], row[0]))[:3]


def test_file_exists():
    assert (BASE/'clearance.json').is_file()


def test_schema():
    data = json.loads((BASE/'clearance.json').read_text())
    assert isinstance(data, list) and len(data) == 3
    assert all(isinstance(row, dict) and set(row) == {'id', 'plate_code', 'clearance_km'} for row in data)
    assert all(isinstance(row['clearance_km'], (int, float)) and not isinstance(row['clearance_km'], bool) for row in data)


def test_ranked_earthquakes():
    data = json.loads((BASE/'clearance.json').read_text())
    assert [row['id'] for row in data] == [row[0] for row in expected()]
    assert all(row['plate_code'] == 'PA' for row in data)


def test_clearances():
    data = json.loads((BASE/'clearance.json').read_text())
    for actual, (_, distance) in zip(data, expected()):
        assert abs(actual['clearance_km'] - round(distance, 2)) <= 0.005
