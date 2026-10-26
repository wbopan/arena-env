#!/bin/bash
set -eu
cat > /tmp/solve_neighbors.py <<'PY'
import json
import math
from pathlib import Path

result = {}
for cif in Path('/root/work/cifs').glob('*.cif'):
    lines = cif.read_text().splitlines()
    lengths = [float(next(s.split()[1] for s in lines if s.startswith('_cell_length_' + axis + ' '))) for axis in 'abc']
    fields = [s for s in lines if s.startswith('_atom_site_')]
    sites = {}
    for text in lines[lines.index(fields[-1]) + 1:]:
        if text.strip():
            row = dict(zip(fields, text.split()))
            sites[row['_atom_site_label']] = [float(row['_atom_site_fract_' + axis]) for axis in 'xyz']
    output = {}
    for label, point in sites.items():
        candidates = []
        for other, target in sites.items():
            if other == label:
                continue
            displacement = [(a - b) - math.floor(a - b + 0.5) for a, b in zip(point, target)]
            d = math.sqrt(sum((v * length) ** 2 for v, length in zip(displacement, lengths)))
            candidates.append((d, other))
        minimum = min(d for d, _ in candidates)
        neighbor = min(other for d, other in candidates if abs(d - minimum) <= 1e-9)
        output[label] = {'neighbor': neighbor, 'distance_angstrom': round(minimum, 4)}
    result[cif.name] = output
Path('/root/work/nearest_sites.json').write_text(json.dumps(result, indent=2) + '\n')
PY
python /tmp/solve_neighbors.py
