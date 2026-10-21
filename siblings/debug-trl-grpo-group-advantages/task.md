# GRPO group-relative advantages from logged rewards

A GRPO run logged per-completion reward components in `/root/work/rewards.csv`. The columns are `prompt_id` (strings such as `p007`), `completion_id` (integers 0-7), `correctness` and `format`. Every prompt has exactly 8 completions, so G = 8. The rows are in arbitrary order.

Recompute the advantages that a correct GRPO trainer would produce.

1. Total reward per completion: `reward = 1.0 * correctness + 0.2 * format`. This is a weighted sum of two reward functions.
2. For each prompt group, compute the group mean `mu` and the **sample** standard deviation `sigma` (Bessel-corrected, divisor G-1). Use only the 8 completions of that prompt.
3. Compute `advantage = (reward - mu) / (sigma + 1e-4)`. The 1e-4 is the numerical-stability epsilon. A group whose rewards are all identical therefore gets advantage 0 for every completion.

Write `/root/work/advantages.csv` with:

- A header row of exactly `prompt_id,completion_id,reward,advantage`.
- One row per input completion.
- Rows sorted by `prompt_id` (string order), then by `completion_id` (numeric ascending).
- `reward` and `advantage` rounded to 6 decimal places.
- No index column.
