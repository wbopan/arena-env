import csv
import json
import math
from pathlib import Path

BASE = Path('/root/work')
FIELDS = ['id', 'boundary_id', 'foot_lon', 'foot_lat', 'distance_km', 'station_km']
SCALE = 6378137 * math.pi / 180 / 1000


def read_rows():
    with (BASE/'footpoints.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == FIELDS
        return list(reader)


def reference():
    lines = json.loads((BASE/'boundaries.geojson').read_text())['features']
    answer = []
    for q in sorted(json.loads((BASE/'earthquakes.json').read_text()), key=lambda r: r['id']):
        choices = []
        px, py = q['longitude'], q['latitude']
        for feature in lines:
            coords = feature['geometry']['coordinates']
            elapsed = 0.0
            for a, b in zip(coords, coords[1:]):
                ux, uy = b[0]-a[0], b[1]-a[1]
                length = math.hypot(ux, uy)
                fraction = max(0.0, min(1.0, ((px-a[0])*ux+(py-a[1])*uy)/(length*length)))
                fx, fy = a[0]+fraction*ux, a[1]+fraction*uy
                choices.append((math.hypot(px-fx, py-fy)*SCALE, feature['properties']['BoundaryID'], fx, fy, (elapsed+fraction*length)*SCALE))
                elapsed += length
        distance, name, fx, fy, station = min(choices)
        answer.append((q['id'], name, fx, fy, distance, station))
    return answer


def test_file_exists():
    assert (BASE/'footpoints.csv').is_file()


def test_header_and_row_count():
    assert len(read_rows()) == len(reference())


def test_ids_and_boundary_selection():
    for row, expected in zip(read_rows(), reference()):
        assert (row['id'], row['boundary_id']) == expected[:2]


def test_closest_coordinates():
    for row, expected in zip(read_rows(), reference()):
        for field, value in zip(('foot_lon', 'foot_lat'), expected[2:4]):
            assert abs(float(row[field]) - round(value, 3)) <= 0.00051


def test_distance_and_station():
    for row, expected in zip(read_rows(), reference()):
        for field, value in zip(('distance_km', 'station_km'), expected[4:]):
            assert abs(float(row[field]) - round(value, 3)) <= 0.00051
