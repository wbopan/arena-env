import random
from pathlib import Path

random.seed(32617)
out = Path('cifs')
out.mkdir(exist_ok=True)
for index in range(2):
    lengths = [round(random.uniform(4.5, 8.5), 3) for _ in range(3)]
    rows = []
    for n in range(7 + index):
        element = random.choice(['Si', 'O', 'Na', 'Cl'])
        xyz = [f'{random.uniform(0.02, 0.98):.5f}' for _ in range(3)]
        rows.append(f'{element}{n + 1} {element} ' + ' '.join(xyz))
    random.shuffle(rows)
    lines = [f'data_neighbors_{index + 1}', *[f'_cell_length_{axis} {length:.3f}' for axis, length in zip('abc', lengths)], '_cell_angle_alpha 90', '_cell_angle_beta 90', '_cell_angle_gamma 90', 'loop_', '_atom_site_label', '_atom_site_type_symbol', '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z', *rows]
    (out / f'neighbors_{index + 1}.cif').write_text('\n'.join(lines) + '\n')
