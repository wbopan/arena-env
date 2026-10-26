import json
from fractions import Fraction
from pathlib import Path

ROOT = Path('/root/work')
OUTPUT = ROOT / 'representatives.json'
COLUMNS = ['_atom_site_label', '_atom_site_Wyckoff_symbol', '_atom_site_symmetry_multiplicity', '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z']


def expected():
    result = {}
    for path in sorted((ROOT / 'cifs').glob('*.cif')):
        lines = path.read_text().splitlines()
        start = lines.index('_atom_site_fract_z') + 1
        positions = {}
        for line in lines[start:]:
            if not line.strip():
                continue
            row = dict(zip(COLUMNS, line.split()))
            letter = row['_atom_site_Wyckoff_symbol']
            if letter not in positions:
                coordinates = []
                for axis in 'xyz':
                    number = Fraction(row[f'_atom_site_fract_{axis}']) % 1
                    coordinates.append(str(number.limit_denominator(12)))
                positions[letter] = {'multiplicity': int(row['_atom_site_symmetry_multiplicity']), 'first_fractional': coordinates}
        result[path.name] = positions
    return result


def load():
    return json.loads(OUTPUT.read_text())


def test_file_exists():
    assert OUTPUT.is_file()


def test_file_and_letter_keys():
    actual = load()
    reference = expected()
    assert set(actual) == set(reference)
    for name in reference:
        assert set(actual[name]) == set(reference[name])


def test_schema():
    for sites in load().values():
        for entry in sites.values():
            assert set(entry) == {'multiplicity', 'first_fractional'}
            assert type(entry['multiplicity']) is int
            assert isinstance(entry['first_fractional'], list) and len(entry['first_fractional']) == 3
            assert all(isinstance(x, str) for x in entry['first_fractional'])


def test_multiplicities():
    for name, sites in expected().items():
        for letter, entry in sites.items():
            assert load()[name][letter]['multiplicity'] == entry['multiplicity']


def test_first_coordinates():
    actual = load()
    for name, sites in expected().items():
        for letter, entry in sites.items():
            assert actual[name][letter]['first_fractional'] == entry['first_fractional']
