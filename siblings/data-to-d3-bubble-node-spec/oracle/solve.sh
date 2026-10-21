#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import csv, json, math
PAL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

def fmt(v):
    for div, s in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if v >= div:
            m = v / div
            return f"{m:.{3 - len(str(int(m)))}f}{s}"
    return str(v)

rows = list(csv.DictReader(open("data/stock-descriptions.csv", newline="")))
secs = sorted({r["sector"] for r in rows if r["sector"] != "ETF"})
if any(r["sector"] == "ETF" for r in rows):
    secs.append("ETF")
col = {s: PAL[i % 10] for i, s in enumerate(secs)}
mx = max(int(r["marketCap"]) for r in rows if r["sector"] != "ETF")
nodes = []
for r in rows:
    etf = r["sector"] == "ETF"
    cap = None if etf else int(r["marketCap"])
    nodes.append({"ticker": r["ticker"], "name": r["name"], "sector": r["sector"], "marketCap": cap,
                  "marketCapLabel": "" if etf else fmt(cap),
                  "radius": 10.0 if etf else round(6 + 34 * math.sqrt(cap / mx), 2),
                  "color": col[r["sector"]], "tooltip": not etf})
order = {s: i for i, s in enumerate(secs)}
nodes.sort(key=lambda n: (order[n["sector"]], -(n["marketCap"] or 0), n["ticker"]))
json.dump({"legend": [{"sector": s, "color": col[s]} for s in secs], "nodes": nodes}, open("bubbles.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
