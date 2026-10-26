#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_urine.py <<'PY'
import csv

with open('spot_urine.csv', newline='') as source, open('urine_ratios.csv', 'w', newline='') as target:
    reader = csv.DictReader(source)
    writer = csv.writer(target)
    writer.writerow(['collection_id', 'uacr_mg_g', 'upcr_mg_g'])
    for r in reader:
        keys = ('albumin_value', 'protein_value', 'creatinine_value')
        if any(not r[k].strip() for k in keys):
            continue
        a, p, c = (float(r[k].strip().replace(',', '.')) for k in keys)
        a *= 10 if r['albumin_unit'] == 'mg/dL' else 1
        p /= 10 if r['protein_unit'] == 'mg/L' else 1
        c *= 11.3 if r['creatinine_unit'] == 'mmol/L' else 1
        writer.writerow([r['collection_id'], f'{a / (c * 0.01):.2f}', f'{1000 * p / c:.2f}'])
PY
python /tmp/solve_urine.py
