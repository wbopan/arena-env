import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path('/root/work')
OUTPUT = ROOT / 'cell_composition.tsv'


def expected():
    totals = {}
    for cif in (ROOT / 'cifs').glob('*.cif'):
        lines = cif.read_text().splitlines()
        start = lines.index('_atom_site_fract_z') + 1
        for line in lines[start:]:
            if not line.strip():
                continue
            label, element, multiplicity, occupancy, *_ = line.split()
            key = (cif.name, element)
            totals[key] = totals.get(key, Decimal('0')) + Decimal(multiplicity) * Decimal(occupancy)
    return totals


def rows():
    with OUTPUT.open(newline='') as f:
        return list(csv.reader(f, delimiter='\t'))


def test_file_exists():
    assert OUTPUT.is_file()


def test_header_and_columns():
    data = rows()
    assert data[0] == ['file', 'element', 'effective_atoms']
    assert all(len(row) == 3 for row in data[1:])


def test_pairs_and_order():
    pairs = [(row[0], row[1]) for row in rows()[1:]]
    assert pairs == sorted(expected())


def test_counts_and_format():
    reference = expected()
    for file, element, value in rows()[1:]:
        assert value.count('.') == 1 and len(value.split('.')[1]) == 3
        assert Decimal(value) == reference[(file, element)]


def test_no_extra_lines():
    assert len(rows()) == len(expected()) + 1
    assert all(row for row in rows())
