import random
from openpyxl import Workbook

random.seed(7231)
proteins = [f'PR{i:03d}' for i in range(1, 13)]
samples = [(f'CL{i:02d}_LUNG_R{i % 3 + 1}', 'Control' if i < 4 else 'Treated') for i in range(8)]
columns = samples[:]
random.shuffle(columns)
wb = Workbook()
data = wb.active
data.title = 'Data'
data.append(['Protein_ID', *(sample for sample, _ in columns)])
for j, protein in enumerate(proteins):
    row = [protein]
    for sample, group in columns:
        value = round(8 + j * 0.23 + (group == 'Treated') * 0.47 + random.uniform(-0.9, 0.9), 5)
        row.append(None if random.random() < 0.17 else value)
    data.append(row)
meta = wb.create_sheet('Metadata')
meta.append(['Sample_ID', 'Group'])
random.shuffle(samples)
for sample, group in samples:
    meta.append([sample, group])
wb.save('expression_panel.xlsx')
