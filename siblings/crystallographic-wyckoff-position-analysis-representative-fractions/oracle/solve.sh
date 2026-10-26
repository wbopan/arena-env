#!/bin/bash
set -eu
cat > /tmp/solve_representatives.py <<'PY'
import json
from fractions import Fraction
from pathlib import Path

result = {}
for path in sorted(Path('/root/work/cifs').glob('*.cif')):
    lines = path.read_text().splitlines()
    header = lines.index('loop_') + 1
    fields = []
    while header < len(lines) and lines[header].startswith('_'):
        fields.append(lines[header]); header += 1
    sites = {}
    for text in lines[header:]:
        if not text.strip():
            continue
        atom = dict(zip(fields, text.split()))
        letter = atom['_atom_site_Wyckoff_symbol']
        if letter in sites:
            continue
        xyz = []
        for axis in 'xyz':
            wrapped = Fraction(atom[f'_atom_site_fract_{axis}']) % 1
            xyz.append(str(wrapped.limit_denominator(12)))
        sites[letter] = {'multiplicity': int(atom['_atom_site_symmetry_multiplicity']), 'first_fractional': xyz}
    result[path.name] = sites
Path('/root/work/representatives.json').write_text(json.dumps(result, indent=2) + '\n')
PY
python /tmp/solve_representatives.py
