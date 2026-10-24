## Reference notes

The Lean proof skills do not apply to this CSV computation. Use Python’s standard-library `csv` and `fractions.Fraction`; avoid floating point, logarithms, and `math.ceil`.

For a row, let `c = a*r/(1-r)`. The geometric-sum identity gives
`S_n = s0 + c*(1-r**n) = L - c*r**n`, where `L = s0 + c`.
Because `c > 0` and `0 < r < 1`, the sequence increases strictly toward `L` but never reaches it. Thus the claim holds exactly when `bound >= L`, including equality.

If it does not hold:
- `bound < s0` means the first violation is `0`.
- Otherwise, find the smallest integer `n` satisfying the **strict** inequality `r**n < (L-bound)/c`. Exponentially double an upper index until the inequality is true, then binary-search between a known nonviolating index and that upper index. Compare `Fraction` values directly; equality is *not* a violation.

Useful API conventions:

```python
import csv
from fractions import Fraction

with open("/root/work/sequences.csv", newline="") as f:
    rows = list(csv.DictReader(f))  # preserves input order; row["id"] stays text

x = Fraction(row["s0"])            # parses signed p/q exactly
text = f"{x.numerator}/{x.denominator}"  # always p/q, even for integers
```

Write with `csv.DictWriter(..., fieldnames=["id", "limit", "holds", "first_violation"])`, call `writeheader()`, and open the output with `newline=""`. Use `"true"`/`"false"` and `""` for an absent violation. After running the script, inspect the header and a few output rows.
