#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import csv, datetime, glob, os
data = {}
for f in sorted(glob.glob("data/indiv-stock/*.csv")):
    t = os.path.splitext(os.path.basename(f))[0]
    rows = [(datetime.date.fromisoformat(r["Date"]), float(r["Close"])) for r in csv.DictReader(open(f, newline=""))]
    data[t] = sorted(rows)
ds = [d for v in data.values() for d, _ in v]
cs = [c for v in data.values() for _, c in v]
d0, d1, c0, c1 = min(ds), max(ds), min(cs), max(cs)
span = (d1 - d0).days
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">']
for i, (t, rows) in enumerate(data.items()):
    pts = [(50 + 530 * (d - d0).days / span, 270 - 250 * (c - c0) / (c1 - c0)) for d, c in rows]
    dstr = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    col = colors[i % len(colors)]
    parts.append(f'<path class="line" data-ticker="{t}" fill="none" stroke="{col}" d="{dstr}"/>')
    lx, ly = pts[-1]
    parts.append(f'<text class="label" data-ticker="{t}" x="{lx + 5:.2f}" y="{ly:.2f}">{t}</text>')
parts.append("</svg>")
open("chart.svg", "w").write("\n".join(parts) + "\n")
EOF
python3 /tmp/solve.py
