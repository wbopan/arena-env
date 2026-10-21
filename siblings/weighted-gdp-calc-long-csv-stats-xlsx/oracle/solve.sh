#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import numpy as np
import pandas as pd
from openpyxl import Workbook
df = pd.read_csv("/root/work/trade_long.csv")
df["bn"] = np.where(df["unit"].str.strip() == "USD mn", df["value"] / 1000.0, df["value"])
p = df.pivot_table(index=["year", "country"], columns="indicator", values="bn", aggfunc="sum")
p["nx"] = (p["exports_gs"] - p["imports_gs"]) / p["gdp_current"] * 100
years = sorted(p.index.get_level_values(0).unique())
wb = Workbook()
ws = wb.active
ws.title = "Stats"
ws["A1"] = "Statistic"
labels = ["Min", "Max", "Median", "Mean", "P25", "P75", "Weighted Mean"]
for i, l in enumerate(labels):
    ws.cell(2 + i, 1, l)
for j, y in enumerate(years):
    t = p.loc[y]
    v = t["nx"].to_numpy()
    g = t["gdp_current"].to_numpy()
    st = [v.min(), v.max(), np.median(v), v.mean(), np.percentile(v, 25), np.percentile(v, 75), np.average(v, weights=g)]
    ws.cell(1, 2 + j, int(y))
    for i, s in enumerate(st):
        ws.cell(2 + i, 2 + j, round(float(s), 3))
wb.save("/root/work/nx_stats.xlsx")
EOF
python3 /tmp/solve.py
