#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_paired_response.py <<'PY'
import csv
from statistics import mean, stdev
from openpyxl import load_workbook

wb = load_workbook('paired_expression.xlsx', data_only=True)
table = list(wb['Data'].values)
positions = {name: i for i, name in enumerate(table[0])}
measurements = {row[0]: row for row in table[1:]}
pairs = list(wb['Pairs'].values)[1:]
targets = [row[0] for row in list(wb['Targets'].values)[1:]]
with open('paired_response.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['protein_id', 'n_pairs', 'mean_log2_delta', 'sd_log2_delta', 'geometric_fold_change'])
    for protein in targets:
        values = measurements[protein]
        deltas = [values[positions[t]] - values[positions[c]] for _, c, t in pairs]
        average = mean(deltas)
        writer.writerow([protein, len(deltas), f'{average:.4f}', f'{stdev(deltas):.4f}', f'{2 ** average:.4f}'])
PY
python /tmp/solve_paired_response.py
