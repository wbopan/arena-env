#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import json, math
import numpy as np
import pandas as pd
from scipy.stats import norm

df = pd.read_csv('/root/work/lake_temps.csv').dropna(subset=['temp_c'])
res = {}
for lid, g in df.groupby('lake_id'):
    g = g.sort_values('year')
    t = g['year'].to_numpy(float)
    x = g['temp_c'].to_numpy(float)
    n = len(x)
    i, j = np.triu_indices(n, k=1)
    d = x[j] - x[i]
    s = float(np.sum(np.sign(d)))
    slope = float(np.median(d / (t[j] - t[i])))
    _, c = np.unique(x, return_counts=True)
    var = (n * (n - 1) * (2 * n + 5) - np.sum(c * (c - 1) * (2 * c + 5))) / 18.0
    z = (s - 1) / math.sqrt(var) if s > 0 else ((s + 1) / math.sqrt(var) if s < 0 else 0.0)
    p = 2 * (1 - norm.cdf(abs(z)))
    tr = 'increasing' if (p < 0.05 and z > 0) else ('decreasing' if (p < 0.05 and z < 0) else 'no trend')
    res[str(lid)] = {'n': int(n), 'sen_slope': round(slope, 4), 'p_value': round(float(p), 4), 'trend': tr}
with open('/root/work/trend_summary.json', 'w') as f:
    json.dump(res, f, indent=2, sort_keys=True)
EOF
python3 /tmp/solve.py
