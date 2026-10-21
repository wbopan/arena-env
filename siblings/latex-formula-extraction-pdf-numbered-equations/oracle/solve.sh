#!/bin/bash
set -e
cat > /tmp/solve_pdf.py <<'EOF'
import json, re
from pypdf import PdfReader
reader = PdfReader("/root/work/tech_note.pdf")
out = []
for pno, page in enumerate(reader.pages, 1):
    for line in (page.extract_text() or "").splitlines():
        m = re.match(r"^\s*(.*?\S)\s+\((\d+)\)\s*$", line)
        if not m:
            continue
        latex = re.sub(r"\s+", " ", m.group(1)).strip().rstrip(",.").strip()
        out.append({"number": int(m.group(2)), "page": pno, "latex": latex})
out.sort(key=lambda d: d["number"])
with open("/root/work/equations.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve_pdf.py
