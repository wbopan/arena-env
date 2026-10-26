#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve_gases.py <<'PY'
import csv
import json

results = []
with open('arterial_gases.csv', newline='') as f:
    for r in csv.DictReader(f):
        def number(field):
            return float(r[field].strip().replace(',', '.'))
        co2 = number('pco2_value')
        oxygen = number('po2_value')
        if r['pco2_unit'] == 'kPa':
            co2 *= 7.5
        if r['po2_unit'] == 'kPa':
            oxygen *= 7.5
        bicarbonate = 0.03 * co2 * 10 ** (number('ph') - 6.1)
        results.append({'sample_id': r['sample_id'], 'pco2_mmHg': f'{co2:.2f}', 'po2_mmHg': f'{oxygen:.2f}', 'bicarbonate_mEq_L': f'{bicarbonate:.2f}'})
with open('gas_results.json', 'w') as f:
    json.dump(results, f, indent=2)
PY
python /tmp/solve_gases.py
