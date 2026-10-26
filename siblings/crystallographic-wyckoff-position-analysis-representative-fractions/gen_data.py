import random
from fractions import Fraction
from pathlib import Path

random.seed(4182)
out = Path('cifs')
out.mkdir(exist_ok=True)
for file_no in range(3):
    letters = random.sample(list('abcdefg'), 3)
    rows = []
    for letter in letters:
        multiplicity = random.choice([2, 4, 6, 8])
        for repeat in range(2):
            coords = []
            for axis in range(3):
                q = Fraction(random.randrange(12), random.randint(2, 12))
                value = float(q) + random.choice([-1, 0, 1]) + random.uniform(-0.00008, 0.00008)
                coords.append(f'{value:.6f}')
            rows.append((f'{letter.upper()}{repeat + 1}', letter, multiplicity, *coords))
    random.shuffle(rows)
    lines = [f'data_sample_{file_no + 1}', '_cell_length_a 5.0', '_cell_length_b 5.0', '_cell_length_c 5.0', '_cell_angle_alpha 90', '_cell_angle_beta 90', '_cell_angle_gamma 90', 'loop_', '_atom_site_label', '_atom_site_Wyckoff_symbol', '_atom_site_symmetry_multiplicity', '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z']
    lines.extend(' '.join(map(str, row)) for row in rows)
    (out / f'sample_{file_no + 1}.cif').write_text('\n'.join(lines) + '\n')
