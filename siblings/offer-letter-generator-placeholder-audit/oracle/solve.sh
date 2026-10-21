#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json, re
from docx import Document

PH = re.compile(r"\{\{([A-Z_]+)\}\}")
doc = Document("offer_letter_template.docx")
data = json.load(open("employee_data.json"))
items = [("body", p.text) for p in doc.paragraphs]

def walk(t):
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                items.append(("table", p.text))
            for nt in cell.tables:
                walk(nt)

for t in doc.tables:
    walk(t)
for s in doc.sections:
    items += [("header", p.text) for p in s.header.paragraphs]
    items += [("footer", p.text) for p in s.footer.paragraphs]

ph, conds = {}, set()
for loc, text in items:
    for n in PH.findall(text):
        if n.startswith("IF_"):
            conds.add(n[3:])
        elif n.startswith("END_IF_"):
            pass
        else:
            e = ph.setdefault(n, {"count": 0, "locations": set()})
            e["count"] += 1
            e["locations"].add(loc)
res = {
    "placeholders": {k: {"count": v["count"], "locations": sorted(v["locations"])} for k, v in sorted(ph.items())},
    "conditions": sorted(conds),
    "missing_keys": sorted(k for k in ph if k not in data),
    "unused_keys": sorted(k for k in data if k not in ph),
}
json.dump(res, open("/root/work/placeholder_audit.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
