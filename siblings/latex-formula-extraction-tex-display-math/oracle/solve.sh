#!/bin/bash
set -e
cat > /tmp/solve_tex.py <<'EOF'
import re
text = open("/root/work/paper.tex").read()
lines = [l for l in text.splitlines() if not l.lstrip().startswith("%")]
src = "\n".join(lines)
pat = re.compile(r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}|\\\[(.*?)\\\]|\$\$(.*?)\$\$", re.S)
out = []
for m in pat.finditer(src):
    body = next(g for g in m.groups() if g is not None)
    body = re.sub(r"\\label\{[^}]*\}", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    body = body.rstrip(",.").strip()
    out.append("$$" + body + "$$")
with open("/root/work/display_formulas.md", "w") as f:
    f.write("\n".join(out) + "\n")
EOF
python3 /tmp/solve_tex.py
