import csv
from pathlib import Path
from PIL import Image

ROOT = Path('/root/work')
OUT = ROOT / 'sprite_locations.csv'
NAMES = ('coin', 'enemy', 'turtle')


def read_rows():
    with OUT.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    return fields, rows


def expected():
    templates = {name: Image.open(ROOT / (name + '.png')).convert('L').tobytes() for name in NAMES}
    found = []
    for number in (1, 2):
        filename = f'frame_{number:03d}.png'
        image = Image.open(ROOT / 'frames' / filename).convert('L')
        for y in range(image.height - 4):
            for x in range(image.width - 4):
                patch = image.crop((x, y, x + 5, y + 5)).tobytes()
                for name in NAMES:
                    if patch == templates[name]:
                        found.append((filename, x, y, name))
    return sorted(found, key=lambda item: (item[0], item[2], item[1]))


def test_file_exists():
    assert OUT.is_file()


def test_header_and_fields():
    fields, rows = read_rows()
    assert fields == ['frame', 'x', 'y', 'kind']
    assert all(set(row) == set(fields) and None not in row.values() for row in rows)


def test_types_and_order():
    _, rows = read_rows()
    assert all(row['frame'] in {'frame_001.png', 'frame_002.png'} and row['kind'] in NAMES for row in rows)
    assert all(row['x'].isdecimal() and row['y'].isdecimal() for row in rows)
    keys = [(r['frame'], int(r['y']), int(r['x'])) for r in rows]
    assert keys == sorted(keys)


def test_locations_and_kinds():
    _, rows = read_rows()
    actual = [(r['frame'], int(r['x']), int(r['y']), r['kind']) for r in rows]
    assert actual == expected()
