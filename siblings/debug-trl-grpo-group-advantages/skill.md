## Reference notes

Use **pandas**; no trainer or model library is needed. GRPO compares each completion only with the other completions sharing its `prompt_id`:

\[
r_i=1.0\,\text{correctness}_i+0.2\,\text{format}_i,\qquad
\mu_p=\frac1G\sum_{i\in p}r_i,\qquad
\sigma_p=\sqrt{\frac{\sum_{i\in p}(r_i-\mu_p)^2}{G-1}},
\qquad A_i=\frac{r_i-\mu_p}{\sigma_p+10^{-4}}.
\]

Here `G=8`. **Sample** standard deviation means `ddof=1`, not NumPy’s default `ddof=0`. Add epsilon *after* calculating the standard deviation; do not add it to the variance.

```python
import pandas as pd

df = pd.read_csv("/root/work/rewards.csv", dtype={"prompt_id": str})
# Calculate the weighted reward column before grouping.
grouped = df.groupby("prompt_id")["reward"]
mu = grouped.transform("mean")             # aligned with the original rows
sigma = grouped.transform("std")            # pandas default: ddof=1
# advantage = (reward - mu) / (sigma + 1e-4)
```

Group by the **ID**, not by adjacent rows: input order is arbitrary. For a constant-reward group, the numerator is zero and epsilon keeps the denominator nonzero.

Before writing, sort with `sort_values(["prompt_id", "completion_id"])`; keep `prompt_id` as a string and `completion_id` numeric. Select columns in the required header order. `to_csv(path, index=False, float_format="%.6f")` emits no index and formats numeric output to six decimal places. Inspect the header and a few output rows after writing.
