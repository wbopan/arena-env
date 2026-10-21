#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import json
import pandas as pd
raw = pd.read_excel("/root/work/gdp.xlsx", sheet_name="Data", header=None)
h = raw.index[raw[1] == "Series Code"][0]
df = raw.iloc[h + 1:].copy()
df.columns = raw.iloc[h].tolist()
df = df.dropna(subset=["Series Code"])
years = [c for c in df.columns if str(c).replace(".0", "").isdigit()]
df["kind"] = df["Series Code"].str[3:]
out = {"countries": {}, "gcc_weighted": {}}
for y in years:
    t = df.pivot(index="Country", columns="kind", values=y).astype(float)
    nx = (t["BXGS_BP6.A"] - t["BMGS_BP6.A"]) / t["NGDPD.A"] * 100
    ys = str(int(float(y)))
    for c, v in nx.items():
        out["countries"].setdefault(c, {})[ys] = round(float(v), 2)
    out["gcc_weighted"][ys] = round(float((nx * t["NGDPD.A"]).sum() / t["NGDPD.A"].sum()), 2)
json.dump(out, open("/root/work/nx_gdp.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
