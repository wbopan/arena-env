#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import json
from pptx import Presentation
prs = Presentation('slides.pptx')
refs = []
idx = {}
for sn, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if sh.is_placeholder or not sh.has_text_frame:
            continue
        paras = sh.text_frame.paragraphs
        runs = [r for p in paras for r in p.runs if r.text.strip()]
        if not runs or any(r.font.italic is not True for r in runs):
            continue
        t = ' '.join(' '.join(''.join(r.text for r in p.runs) for p in paras).split())
        k = t.lower()
        if k not in idx:
            idx[k] = len(refs)
            refs.append({'number': len(refs) + 1, 'title': t, 'slides': []})
        if sn not in refs[idx[k]]['slides']:
            refs[idx[k]]['slides'].append(sn)
json.dump({'references': refs}, open('references.json', 'w'), indent=2)
EOF
python3 /tmp/solve.py
