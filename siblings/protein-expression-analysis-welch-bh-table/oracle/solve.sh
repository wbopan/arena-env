#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py <<'EOF'
import pandas as pd, numpy as np
from scipy import stats
f = "protein_expression.xlsx"
d = pd.read_excel(f, sheet_name="Data").set_index("Protein_ID")
g = pd.read_excel(f, sheet_name="Design")
c = g.loc[g.Group == "Control", "Sample"].tolist()
t = g.loc[g.Group == "Treated", "Sample"].tolist()
mc = d[c].mean(axis=1).values
mt = d[t].mean(axis=1).values
p = stats.ttest_ind(d[t].values, d[c].values, axis=1, equal_var=False).pvalue
m = len(p)
o = np.argsort(p)
r = p[o] * m / np.arange(1, m + 1)
r = np.minimum.accumulate(r[::-1])[::-1]
q = np.empty(m)
q[o] = np.minimum(r, 1)
lf = mt - mc
out = pd.DataFrame({"protein_id": d.index, "mean_control": mc, "mean_treated": mt, "log2fc": lf, "p_value": p, "q_value": q})
out["significant"] = np.where((out.q_value < 0.05) & (out.log2fc.abs() >= 1), "yes", "no")
out.to_csv("results.csv", index=False, float_format="%.12g")
EOF
python3 /tmp/solve.py
