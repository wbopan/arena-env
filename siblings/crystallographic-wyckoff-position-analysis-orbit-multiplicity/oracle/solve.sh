#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import glob, json, os, re, shlex
from fractions import Fraction
import numpy as np

def loops_of(path):
    L = open(path).read().splitlines()
    out = []; i = 0
    while i < len(L):
        if L[i].strip() == 'loop_':
            i += 1; hdr = []
            while i < len(L) and L[i].strip().startswith('_'):
                hdr.append(L[i].strip()); i += 1
            rows = []
            while i < len(L):
                t = L[i].strip()
                if not t or t == 'loop_' or t.startswith('_') or t.startswith('data_'):
                    break
                rows.append(shlex.split(t)); i += 1
            out.append((hdr, rows))
        else:
            i += 1
    return out

num = lambda s: float(re.sub(r'\(.*?\)', '', s))
res = {}
for path in sorted(glob.glob('cifs/*.cif')):
    ops = atoms = None
    for hdr, rows in loops_of(path):
        if '_symmetry_equiv_pos_as_xyz' in hdr:
            k = hdr.index('_symmetry_equiv_pos_as_xyz')
            ops = [[c.strip() for c in r[k].split(',')] for r in rows]
        if '_atom_site_label' in hdr:
            atoms = [dict(zip(hdr, r)) for r in rows]
    sites = {}; content = {}
    for a in atoms:
        p0 = [num(a['_atom_site_fract_' + ax]) for ax in 'xyz']
        imgs = []
        for op in ops:
            env = dict(x=p0[0], y=p0[1], z=p0[2])
            p = np.array([eval(c, {}, env) for c in op]) % 1.0
            if not any(np.all(np.abs((p - q) - np.round(p - q)) < 1e-3) for q in imgs):
                imgs.append(p)
        m = len(imgs)
        occ = num(a['_atom_site_occupancy'])
        el = a['_atom_site_type_symbol']
        content[el] = content.get(el, 0.0) + m * occ
        sites[a['_atom_site_label']] = {'multiplicity': m,
            'fract': [str(Fraction(v % 1.0).limit_denominator(12)) for v in p0]}
    res[os.path.basename(path)] = {'n_symops': len(ops), 'sites': sites,
        'cell_content': {k: round(v, 3) for k, v in content.items()}}
json.dump(res, open('wyckoff_summary.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
