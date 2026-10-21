#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import pandas as pd, numpy as np
from openpyxl import Workbook
f = "raw_intensity.xlsx"
d = pd.read_excel(f, sheet_name="Data").set_index("Protein_ID").astype(float)
d = np.log2(d.where(d > 0))
d = d - d.median()
s = pd.read_excel(f, sheet_name="Samples")
m = dict(zip(s.Sample_ID, s.Condition))
g = pd.Series({c: m[c.rsplit("_", 1)[1]] for c in d.columns})
C = g[g == "Control"].index
T = g[g == "Treated"].index
tg = pd.read_excel(f, sheet_name="Targets").Protein_ID
wb = Workbook()
ws = wb.active
ws.title = "Summary"
ws.append(["Protein_ID", "N_Control", "N_Treated", "Mean_Control", "Mean_Treated", "Log2FC", "Fold_Change"])
for p in tg:
    r = d.loc[p]
    mc = float(r[C].mean()); mt = float(r[T].mean()); l = mt - mc
    ws.append([p, int(r[C].notna().sum()), int(r[T].notna().sum()), round(mc, 4), round(mt, 4), round(l, 4), round(2 ** l, 4)])
wb.save("target_summary.xlsx")
EOF
python3 /tmp/solve.py
