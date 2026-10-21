#!/bin/bash
set -e
cat > /tmp/solve.py << 'EOF'
import numpy as np
import pandas as pd

df = pd.read_csv("/root/work/grid_counts.csv")
m = df["n_matched"]
df["f1"] = np.where(m > 0, 2 * m / (df["n_clusters"] + df["n_expert"]), 0.0)
df["dl"] = df["sum_dist"] / m.where(m > 0)
keys = ["min_samples", "epsilon", "shape_weight"]
agg = df.groupby(keys).agg(F1=("f1", "mean"), delta=("dl", "mean")).reset_index()
agg = agg[agg["F1"] > 0.5].dropna(subset=["delta"]).reset_index(drop=True)
F = agg["F1"].to_numpy()
D = agg["delta"].to_numpy()
keep = []
for i in range(len(agg)):
    dom = (F >= F[i]) & (D <= D[i]) & ((F > F[i]) | (D < D[i]))
    keep.append(not dom.any())
fr = agg[np.array(keep, dtype=bool)].sort_values(["F1", "delta"], ascending=[False, True])
fr = fr[["F1", "delta", "min_samples", "epsilon", "shape_weight"]].copy()
fr["F1"] = fr["F1"].round(5)
fr["delta"] = fr["delta"].round(5)
fr["shape_weight"] = fr["shape_weight"].round(1)
fr["min_samples"] = fr["min_samples"].astype(int)
fr["epsilon"] = fr["epsilon"].astype(int)
fr.to_csv("/root/work/pareto.csv", index=False)
EOF
python3 /tmp/solve.py
