#!/bin/bash
set -e
cd /root/work
cat > /tmp/redact.py <<'EOF'
import re
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, TextStringObject

SRC = "register.pdf"
DST = "register_redacted.pdf"
PAT = re.compile(r"(?<!\d)\d{10}(?!\d)")


def mask(m):
    return "******" + m.group(0)[-4:]


def lines(page):
    t = page.extract_text() or ""
    return [PAT.sub(mask, re.sub(r"\s+", " ", l).strip()) for l in t.splitlines() if l.strip()]


def edit_streams():
    w = PdfWriter(clone_from=SRC)
    for page in w.pages:
        cs = ContentStream(page.get_contents(), w)
        ops = cs.operations
        for operands, op in ops:
            if op == b"Tj" and operands and isinstance(operands[0], str):
                operands[0] = TextStringObject(PAT.sub(mask, operands[0]))
            elif op == b"TJ" and operands:
                arr = operands[0]
                for i, x in enumerate(arr):
                    if isinstance(x, str):
                        arr[i] = TextStringObject(PAT.sub(mask, x))
        cs.operations = ops
        page.replace_contents(cs)
    with open(DST, "wb") as f:
        w.write(f)


def ok():
    src, out = PdfReader(SRC), PdfReader(DST)
    if len(src.pages) != len(out.pages):
        return False
    for a, b in zip(src.pages, out.pages):
        if lines(a) != lines(b):
            return False
        if PAT.search(b.extract_text() or ""):
            return False
    return True


def rebuild():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(DST, pagesize=letter)
    for p in PdfReader(SRC).pages:
        y = 740
        c.setFont("Helvetica", 10)
        for l in lines(p):
            c.drawString(72, y, l)
            y -= 20
        c.showPage()
    c.save()


try:
    edit_streams()
    good = ok()
except Exception:
    good = False
if not good:
    rebuild()
EOF
python3 /tmp/redact.py
