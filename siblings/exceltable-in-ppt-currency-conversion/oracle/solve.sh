#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import zipfile, io, re, json
from openpyxl import load_workbook
from pptx import Presentation
p = '/root/work/report.pptx'
z = zipfile.ZipFile(p)
n = [x for x in z.namelist() if x.startswith('ppt/embeddings/') and x.endswith('.xlsx')][0]
ws = load_workbook(io.BytesIO(z.read(n))).worksheets[0]
def val(c):
    v = c.value
    if isinstance(v, str) and v.startswith('='):
        m = re.fullmatch(r'=1/([A-Z]+[0-9]+)', v.replace(' ', '').replace('$', ''))
        return 1 / val(ws[m.group(1)])
    return float(v)
hdr = {ws.cell(1, j).value: j for j in range(2, ws.max_column + 1)}
rows = {ws.cell(i, 1).value: i for i in range(2, ws.max_row + 1)}
text = None
for sh in Presentation(p).slides[0].shapes:
    if sh.has_text_frame and sh.text_frame.text.strip().startswith('Report currency:'):
        text = sh.text_frame.text
lines = [l.strip() for l in text.splitlines() if l.strip()]
tgt = lines[0].split(':', 1)[1].strip()
conv = {}
for l in lines[1:]:
    name, rest = l.split(':', 1)
    a, code = rest.split()
    r = 1.0 if code == tgt else val(ws.cell(rows[code], hdr[tgt]))
    conv[name.strip()] = round(float(a.replace(',', '')) * r, 2)
json.dump({'report_currency': tgt, 'converted': conv, 'total': round(sum(conv.values()), 2)}, open('/root/work/converted.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
