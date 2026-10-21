#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json, re
from docx import Document

d = json.load(open("employee_data.json"))
F, C = d["fields"], d["conditions"]
doc = Document("offer_letter_template.docx")
PH = re.compile(r"\{\{([A-Z_]+)\}\}")
MARK = re.compile(r"^\{\{(END_)?IF_([A-Z_]+)\}\}$")

cur, rm = None, []
for p in doc.paragraphs:
    m = MARK.match(p.text.strip())
    if m:
        rm.append(p)
        cur = None if m.group(1) else m.group(2)
        continue
    if cur is not None and C.get(cur) != "Yes":
        rm.append(p)
for p in rm:
    p._element.getparent().remove(p._element)

def fix(p):
    t = p.text
    if "{{" not in t:
        return
    n = PH.sub(lambda m: str(F.get(m.group(1), m.group(0))), t)
    if p.runs:
        p.runs[0].text = n
        for r in p.runs[1:]:
            r.text = ""

def walk(t):
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                fix(p)
            for nt in cell.tables:
                walk(nt)

for p in doc.paragraphs:
    fix(p)
for t in doc.tables:
    walk(t)
for s in doc.sections:
    for p in s.header.paragraphs:
        fix(p)
    for p in s.footer.paragraphs:
        fix(p)
doc.save("/root/work/offer_letter_filled.docx")
EOF
python3 /tmp/solve.py
