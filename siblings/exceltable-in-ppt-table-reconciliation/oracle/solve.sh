#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import zipfile, io, re, csv
from openpyxl import load_workbook
from pptx import Presentation
p = '/root/work/budget.pptx'
z = zipfile.ZipFile(p)
n = [x for x in z.namelist() if x.startswith('ppt/embeddings/') and x.endswith('.xlsx')][0]
ws = load_workbook(io.BytesIO(z.read(n))).worksheets[0]
def ev(v):
    if isinstance(v, str) and v.startswith('='):
        rng = re.search(r'[(](.*)[)]', v).group(1).replace('$', '')
        return sum(ev(c.value) for row in ws[rng] for c in row)
    return int(v)
hdr = [c.value for c in ws[1]]
book = {}
for r in ws.iter_rows(min_row=2):
    if r[0].value:
        book[r[0].value] = {hdr[k]: ev(r[k].value) for k in range(1, len(hdr))}
tbl = [s for s in Presentation(p).slides[0].shapes if s.has_table][0].table
th = [c.text for c in tbl.rows[0].cells]
out = [['department', 'column', 'slide_value', 'workbook_value']]
for row in list(tbl.rows)[1:]:
    cs = [c.text.strip() for c in row.cells]
    for j in range(1, len(th)):
        sv = int(cs[j].replace(',', ''))
        wv = book[cs[0]][th[j]]
        if sv != wv:
            out.append([cs[0], th[j], sv, wv])
with open('/root/work/mismatches.csv', 'w', newline='') as f:
    csv.writer(f).writerows(out)
EOF
python3 /tmp/solve.py
