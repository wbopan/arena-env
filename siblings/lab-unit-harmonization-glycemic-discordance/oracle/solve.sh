#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_glycemic.py <<'PY'
import csv

with open('glycemic_pairs.csv', newline='') as source, open('glycemic_comparison.csv', 'w', newline='') as target:
    writer = csv.writer(target)
    writer.writerow(['patient_id', 'hba1c_percent', 'eag_mg_dL', 'glucose_mg_dL', 'gap_mg_dL'])
    for row in csv.DictReader(source):
        h = float(row['hba1c_value'].strip().replace(',', '.'))
        glucose = float(row['glucose_value'].strip().replace(',', '.'))
        if row['hba1c_unit'] == 'IFCC_mmol_mol':
            h = h / 10.929 + 2.15
        if row['glucose_unit'] == 'mmol/L':
            glucose *= 18.02
        eag = 28.7 * h - 46.7
        writer.writerow([row['patient_id'], f'{h:.2f}', f'{eag:.2f}', f'{glucose:.2f}', f'{glucose - eag:.2f}'])
PY
python /tmp/solve_glycemic.py
