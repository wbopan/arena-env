## Reference notes

Use Python’s standard-library `csv` and `json` modules. Read with `csv.DictReader` to preserve input-row order; write a JSON **array**, not JSON Lines.

```python
import csv, json

with open(input_path, newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def number(cell):
    return float(cell.strip().replace(',', '.'))

def mmhg(value, unit):
    return value * 7.5 if unit.strip() == 'kPa' else value
```

- Parse `ph`, `pco2_value`, and `po2_value` separately. pH is dimensionless: parse it, but do not convert it.
- Apply each pressure’s **own** unit label. `mmHg` values remain unchanged; multiply `kPa` values by `7.5`. Do not infer units from physiological ranges.
- From the **unrounded** converted pCO2, estimate bicarbonate as `0.03 * pco2_mmHg * 10 ** (ph - 6.1)`. Round only when formatting each output field.
- Format numeric strings with `f"{value:.2f}"`. Each object should contain exactly `sample_id`, `pco2_mmHg`, `po2_mmHg`, and `bicarbonate_mEq_L`; keep `sample_id` as a string.
- Write once with `json.dump(results, f)`. Samples are complete, so do not filter rows or clamp values.
