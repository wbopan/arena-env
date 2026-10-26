#!/bin/bash
set -euo pipefail
cd /root/work
cat > /tmp/solve_sample_qc.py <<'PY'
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

wb = load_workbook('expression_panel.xlsx')
data = wb['Data']
metadata = wb['Metadata']
positions = {data.cell(1, col).value: col for col in range(2, data.max_column + 1)}
qc = wb.create_sheet('QC')
qc.append(['Sample_ID', 'Group', 'Detected_Proteins', 'Mean_Log2', 'SD_Log2'])
for sample, group in list(metadata.values)[1:]:
    letter = get_column_letter(positions[sample])
    region = f'Data!{letter}2:{letter}{data.max_row}'
    qc.append([sample, group, f'=COUNT({region})', f'=AVERAGE({region})', f'=STDEV({region})'])
    for col in (4, 5):
        qc.cell(qc.max_row, col).number_format = '0.0000'
wb.save('sample_qc.xlsx')
PY
python /tmp/solve_sample_qc.py
