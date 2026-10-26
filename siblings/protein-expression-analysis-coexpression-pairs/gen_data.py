import random
from openpyxl import Workbook

random.seed(9506)
proteins = [f'CO{i:02d}' for i in range(1, 9)]
samples = [f'CELL_{i:02d}_REP' for i in range(1, 7)]
latent = [random.uniform(-2.0, 2.0) for _ in samples]
profiles = {}
for j, protein in enumerate(proteins):
    slope = random.choice([-1, 1]) * random.uniform(0.45, 1.5)
    profiles[protein] = {sample: round(9 + j * 0.4 + slope * latent[i] + random.uniform(-0.8, 0.8), 5) for i, sample in enumerate(samples)}
pairs = [('LINK_A', 'CO01', 'CO02'), ('LINK_B', 'CO03', 'CO04'), ('LINK_C', 'CO05', 'CO06'), ('LINK_D', 'CO01', 'CO07'), ('LINK_E', 'CO02', 'CO08'), ('LINK_F', 'CO04', 'CO06')]
random.shuffle(pairs)
random.shuffle(samples)
random.shuffle(proteins)
wb = Workbook()
data = wb.active
data.title = 'Data'
data.append(['Protein_ID', *samples])
for protein in proteins:
    data.append([protein, *(profiles[protein][sample] for sample in samples)])
ws = wb.create_sheet('Pairs')
ws.append(['Pair_ID', 'Protein_A', 'Protein_B'])
for entry in pairs:
    ws.append(entry)
wb.save('coexpression_panel.xlsx')
