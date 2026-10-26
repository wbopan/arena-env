import csv
import random

random.seed(412)

def text(x, i):
    s = f'{x:.3f}'
    if i % 3 == 0:
        s = f'{x:.3e}'
    elif i % 3 == 1:
        s = s.replace('.', ',')
    return f' {s} ' if i % 2 else s

with open('spot_urine.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['collection_id', 'albumin_value', 'albumin_unit', 'protein_value', 'protein_unit', 'creatinine_value', 'creatinine_unit'])
    for i in range(18):
        albumin = random.randint(15, 850) / 10
        protein = random.randint(30, 1200) / 10
        creat = random.randint(45, 230)
        au = 'mg/dL' if i % 2 else 'mg/L'
        pu = 'mg/L' if i % 3 else 'mg/dL'
        cu = 'mmol/L' if i % 4 < 2 else 'mg/dL'
        av = albumin / 10 if au == 'mg/dL' else albumin
        pv = protein * 10 if pu == 'mg/L' else protein
        cv = creat / 11.3 if cu == 'mmol/L' else creat
        vals = [text(av, i), text(pv, i + 1), text(cv, i + 2)]
        if i in (4, 13):
            vals[0 if i == 4 else 2] = ''
        w.writerow([f'U{i+1:03}', vals[0], au, vals[1], pu, vals[2], cu])
