import numpy as np
import pandas as pd

rng = np.random.default_rng(99)
images = [f"orbit{4200 + 11 * i}_rad" for i in range(9)]
n_exp = {im: int(rng.integers(3, 8)) for im in images}
empty = {images[6]}
rows = []
for ms in [3, 5, 7]:
    for eps in [6, 12, 18, 24]:
        for w in [1.0, 1.4, 1.8]:
            for im in images:
                ne = n_exp[im]
                if im in empty:
                    rows.append((ms, eps, w, im, 0, ne, 0, 0.0))
                    continue
                r = 0.45 + 0.025 * eps - 0.04 * (ms - 3) - 0.25 * abs(w - 1.3) + rng.normal(0, 0.05)
                r = float(np.clip(r, 0.05, 1.0))
                m = int(rng.binomial(ne, r))
                nc = m + int(rng.poisson(0.3 + eps / 12 + 0.1 * (6 - ms)))
                if m:
                    sd = m * (1.5 + 0.35 * eps + 4 * abs(w - 1.3)) * float(rng.lognormal(0, 0.15))
                else:
                    sd = 0.0
                rows.append((ms, eps, w, im, nc, ne, m, round(sd, 4)))

cols = ["min_samples", "epsilon", "shape_weight", "file_rad", "n_clusters", "n_expert", "n_matched", "sum_dist"]
pd.DataFrame(rows, columns=cols).to_csv("grid_counts.csv", index=False)
