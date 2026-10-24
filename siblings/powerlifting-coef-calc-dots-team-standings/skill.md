## Reference notes

Use Python’s standard-library `csv` and `json`; no powerlifting package is needed.

- Read the headered CSV with `csv.DictReader`. Its values are strings; an empty lift is `''`, so check before calling `float()`.
- A lifter bombs out if **any** of `Best3SquatKg`, `Best3BenchKg`, or `Best3DeadliftKg` is empty or converts to a value `<= 0`. Assign Dots `0`, rather than summing the remaining lifts.
- For valid lifts, `TotalKg` is their sum. Use the **men’s** coefficients for both `M` and `Mx`, and the women’s for `F`. Clamp bodyweight before evaluating the polynomial:

```python
x = min(max(float(bodyweight), lower_bound), upper_bound)
denominator = (((A*x + B)*x + C)*x + D)*x + E
dots = total_kg * 500 / denominator
```

  Bounds: `M`/`Mx` `[40, 210]`; `F` `[40, 150]`. Coefficients `(A, B, C, D, E)` are listed in the task; keep their signs and precision. This is **DOTS**, not Wilks or IPF Goodlift.

- Group `(name, dots)` by team. Sort each team’s members by **unrounded** Dots descending and take the first three. Sum those three unrounded values; sort teams by those unrounded sums descending. Only then use `round(score, 2)` for the JSON score. Assign consecutive integer ranks starting at 1.
- Output is a JSON **array**, not CSV or newline-delimited JSON. Each object should contain only `rank`, `team`, `score`, `top_lifters`; names in `top_lifters` follow the counted members’ Dots order.

Minimal I/O pattern:

```python
with open('/root/work/lifters.csv', newline='', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

with open('/root/work/team_standings.json', 'w', encoding='utf-8') as f:
    json.dump(standings, f, ensure_ascii=False, indent=2)
```

Inspect the CSV header and a few rows cheaply, write one script, run it, then read back the JSON to confirm its structure and ordering.
