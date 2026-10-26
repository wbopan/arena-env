import json
import math
from pathlib import Path

ROOT = Path('/root/work')
OUTPUT = ROOT / 'nearest_sites.json'


def expected():
    answer = {}
    for cif in sorted((ROOT / 'cifs').glob('*.cif')):
        lines = cif.read_text().splitlines()
        cell = [float(next(line.split()[1] for line in lines if line.startswith('_cell_length_' + axis + ' '))) for axis in 'abc']
        start = lines.index('_atom_site_fract_z') + 1
        sites = {}
        for line in lines[start:]:
            if line.strip():
                label, species, *xyz = line.split()
                sites[label] = tuple(map(float, xyz))
        nearest = {}
        for label, xyz in sites.items():
            candidates = []
            for other, uvw in sites.items():
                if other == label:
                    continue
                delta = [abs(a - b) for a, b in zip(xyz, uvw)]
                distance = math.sqrt(sum((min(d, 1 - d) * length) ** 2 for d, length in zip(delta, cell)))
                candidates.append((distance, other))
            shortest = min(distance for distance, _ in candidates)
            chosen = min(other for distance, other in candidates if abs(distance - shortest) <= 1e-9)
            nearest[label] = (chosen, shortest)
        answer[cif.name] = nearest
    return answer


def load():
    return json.loads(OUTPUT.read_text())


def test_file_exists():
    assert OUTPUT.is_file()


def test_complete_keys():
    data = load()
    reference = expected()
    assert set(data) == set(reference)
    for file in reference:
        assert set(data[file]) == set(reference[file])


def test_schema():
    for sites in load().values():
        for record in sites.values():
            assert set(record) == {'neighbor', 'distance_angstrom'}
            assert isinstance(record['neighbor'], str)
            assert type(record['distance_angstrom']) in (int, float)
            assert record['distance_angstrom'] >= 0


def test_neighbor_labels():
    for file, sites in expected().items():
        for label, (neighbor, _) in sites.items():
            assert load()[file][label]['neighbor'] == neighbor


def test_distances():
    data = load()
    for file, sites in expected().items():
        for label, (_, distance) in sites.items():
            actual = data[file][label]['distance_angstrom']
            assert abs(actual - round(distance, 4)) <= 1e-9
