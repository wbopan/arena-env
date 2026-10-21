#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import csv, os, re
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
KW = {
    'LLM': ['transformer', 'token', 'prompt', 'finetuning', 'attention'],
    'trapped_ion_and_qc': ['ion', 'qubit', 'laser', 'entanglement', 'trap'],
    'black_hole': ['horizon', 'accretion', 'schwarzschild', 'hawking', 'singularity'],
    'DNA': ['nucleotide', 'helix', 'genome', 'polymerase', 'sequencing'],
    'music_history': ['baroque', 'symphony', 'composer', 'opera', 'renaissance'],
}
out = []
for f in sorted(os.listdir('inbox')):
    p = os.path.join('inbox', f)
    if f.endswith('.pdf'):
        r = PdfReader(p); text = ' '.join(pg.extract_text() or '' for pg in r.pages); u = len(r.pages)
    elif f.endswith('.docx'):
        ps = [x.text for x in Document(p).paragraphs]; text = ' '.join(ps); u = sum(1 for t in ps if t.strip())
    elif f.endswith('.pptx'):
        prs = Presentation(p); u = len(prs.slides)
        text = ' '.join(sh.text_frame.text for s in prs.slides for sh in s.shapes if sh.has_text_frame)
    else:
        continue
    toks = re.findall(r'[a-z]+', text.lower())
    sc = {s: sum(toks.count(k) for k in ks) for s, ks in KW.items()}
    out.append((f, min(sc, key=lambda s: (-sc[s], s)), u))
with open('manifest.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['file', 'subject', 'units']); w.writerows(out)
EOF
python3 /tmp/solve.py
