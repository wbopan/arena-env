#!/bin/bash
set -eu
cat > /tmp/solve_composition.py <<'PY'
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

counts = defaultdict(Decimal)
for cif in Path('/root/work/cifs').glob('*.cif'):
    lines = cif.read_text().splitlines()
    fields = [line for line in lines if line.startswith('_atom_site_')]
    start = lines.index(fields[-1]) + 1
    for line in lines[start:]:
        if not line.strip():
            continue
        site = dict(zip(fields, line.split()))
        key = (cif.name, site['_atom_site_type_symbol'])
        counts[key] += Decimal(site['_atom_site_symmetry_multiplicity']) * Decimal(site['_atom_site_occupancy'])
output = ['file\telement\teffective_atoms']
for (file, element), count in sorted(counts.items()):
    output.append(f'{file}\t{element}\t{count:.3f}')
Path('/root/work/cell_composition.tsv').write_text('\n'.join(output) + '\n')
PY
python /tmp/solve_composition.py
