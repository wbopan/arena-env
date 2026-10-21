# Exact bound checks for geometric partial-sum sequences

Before attempting Lean proofs of the form `S n ≤ B` for all `n`, we want to know which claims are actually true.

## Input

The file `/root/work/sequences.csv` has the columns `id,s0,a,r,bound`. Each value is an exact rational written as `p/q`, and may be negative.

Each row defines a sequence:

- S_0 = s0
- S_{n+1} = S_n + a * r^(n+1), for every natural number n

In every row, a > 0 and 0 < r < 1.

The row's claim is: S_n ≤ bound for all n ≥ 0.

## What to compute

For each row, compute:

- `limit`: the exact limit of S_n as n tends to infinity.
- `holds`: `true` if the claim holds for every n ≥ 0, otherwise `false`.
- `first_violation`: the smallest n ≥ 0 with S_n > bound. Leave it empty when `holds` is `true`.

Use exact rational arithmetic. Floating point is not acceptable, because some bounds lie exactly at, or extremely close to, the critical values.

## Output

Write `/root/work/bounds_report.csv`.

- The header must be exactly `id,limit,holds,first_violation`.
- There must be one row per input row, in the same order as the input.
- `limit` must be written as `p/q` in lowest terms with q ≥ 1. Integers use q = 1, for example `2/1`.
- `holds` must be lowercase `true` or `false`.
- `first_violation` must be a plain decimal integer, or empty.
