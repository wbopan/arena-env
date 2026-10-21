#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
prs = Presentation('deck.pptx')
W, H = prs.slide_width, prs.slide_height
seen, order = set(), []
for s in prs.slides:
    for sh in s.shapes:
        if sh.is_placeholder or not sh.has_text_frame:
            continue
        t = ' '.join(sh.text_frame.text.split())
        if not t or t.startswith('Note:'):
            continue
        sh.left = 457200
        sh.top = H - 685800
        sh.width = W - 914400
        sh.height = 457200
        for p in sh.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.name = 'Arial'
                r.font.size = Pt(16)
                r.font.bold = False
                r.font.color.rgb = RGBColor(0x98, 0x95, 0x96)
        if t.lower() not in seen:
            seen.add(t.lower())
            order.append(t)
layout = [l for l in prs.slide_layouts if l.name == 'Title and Content'][0]
s = prs.slides.add_slide(layout)
s.shapes.title.text = 'Reference'
tf = s.placeholders[1].text_frame
for i, t in enumerate(order):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = t
    pPr = p._p.get_or_add_pPr()
    for c in list(pPr):
        if c.tag in (qn('a:buNone'), qn('a:buChar'), qn('a:buAutoNum')):
            pPr.remove(c)
    pPr.append(pPr.makeelement(qn('a:buAutoNum'), {'type': 'arabicPeriod'}))
prs.save('deck_processed.pptx')
EOF
python3 /tmp/solve.py
