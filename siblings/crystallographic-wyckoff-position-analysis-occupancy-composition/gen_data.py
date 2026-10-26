import random
from pathlib import Path

random.seed(9071)
out = Path('cifs')
out.mkdir(exist_ok=True)
for index in range(2):
    rows = []
    elements = random.sample(['Al', 'Fe', 'O', 'S', 'Ti', 'Zn'], 4)
    for n in range(9):
        element = random.choice(elements)
        multiplicity = random.choice([2, 4, 6, 8])
        occupancy = random.choice([0.125, 0.250, 0.375, 0.500, 0.625, 0.750, 0.875, 1.000])
        coords = [f'{random.random():.5f}' for _ in range(3)]
        rows.append(f'{element}{n + 1} {element} {multiplicity} {occupancy:.3f} ' + ' '.join(coords))
    random.shuffle(rows)
    text = [f'data_cell_{index + 1}', '_cell_length_a 6.0', '_cell_length_b 7.0', '_cell_length_c 8.0', '_cell_angle_alpha 90', '_cell_angle_beta 90', '_cell_angle_gamma 90', 'loop_', '_atom_site_label', '_atom_site_type_symbol', '_atom_site_symmetry_multiplicity', '_atom_site_occupancy', '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z', *rows]
    (out / f'cell_{index + 1}.cif').write_text('\n'.join(text) + '\n')
