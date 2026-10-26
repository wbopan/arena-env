import csv
import random

random.seed(7723)

def render(value, i):
    if i % 4 == 0:
        s = f'{value:.5e}'
    else:
        s = f'{value:.3f}'
        if i % 4 == 1:
            s = s.replace('.', ',')
    return f'  {s} ' if i % 3 == 0 else s

with open('glycemic_pairs.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['patient_id', 'hba1c_value', 'hba1c_unit', 'glucose_value', 'glucose_unit'])
    for i in range(20):
        percent = random.randint(48, 123) / 10
        glucose = random.randint(78, 310)
        hu = 'IFCC_mmol_mol' if i % 3 else 'NGSP_percent'
        gu = 'mmol/L' if i % 2 else 'mg/dL'
        hv = (percent - 2.15) * 10.929 if hu == 'IFCC_mmol_mol' else percent
        gv = glucose / 18.02 if gu == 'mmol/L' else glucose
        w.writerow([f'P{i+1:03}', render(hv, i), hu, render(gv, i + 1), gu])
