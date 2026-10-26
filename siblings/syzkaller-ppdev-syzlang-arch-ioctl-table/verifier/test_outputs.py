import csv
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'ioctl_numbers.csv'


def read_csv(path):
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def expected(row, arch):
    direction = {'IO': 0, 'IOW': 1, 'IOR': 2, 'IOWR': 3}[row['direction']]
    return (direction * (2 ** 30) + int(row['size_' + arch]) * (2 ** 16)
            + int(row['type'], 16) * 256 + int(row['nr'], 16))


def test_file_exists():
    assert OUT.is_file()


def test_schema_and_row_order():
    header, actual = read_csv(OUT)
    _, source = read_csv(ROOT / 'ioctl_layout.csv')
    assert header == ['name', '386', 'amd64']
    assert [r['name'] for r in actual] == [r['name'] for r in source]


def test_386_values():
    _, actual = read_csv(OUT)
    _, source = read_csv(ROOT / 'ioctl_layout.csv')
    assert [r['386'] for r in actual] == [str(expected(r, '386')) for r in source]


def test_amd64_values():
    _, actual = read_csv(OUT)
    _, source = read_csv(ROOT / 'ioctl_layout.csv')
    assert [r['amd64'] for r in actual] == [str(expected(r, 'amd64')) for r in source]
