## Reference notes

Use Python’s standard-library `csv` and `decimal` modules. `csv.DictReader` preserves row order and reads columns by name; `csv.DictWriter(..., fieldnames=[...])` fixes the output column order. Open CSV files with `newline=''`.

```python
from decimal import Decimal

def number(raw):
    s = raw.strip()
    return None if not s else Decimal(s.replace(',', '.'))
```

This handles surrounding whitespace, comma decimals, and scientific notation. Check all three numeric fields for emptiness before calculating; do not filter on the size of a resulting ratio.

Convert according to the **unit label**, not an expected clinical range:

- Albumin → mg/L: multiply `mg/dL` by `10`; leave `mg/L` unchanged.
- Protein → mg/dL: divide `mg/L` by `10`; leave `mg/dL` unchanged.
- Urine creatinine → mg/dL: multiply `mmol/L` by `11.3`; leave `mg/dL` unchanged. Use the exercise’s **11.3** factor, not the conflicting urine-creatinine factor in the reference table.

With those converted concentrations:

```python
creatinine_g_L = creatinine_mg_dL * Decimal('0.01')
uacr_mg_g = albumin_mg_L / creatinine_g_L
upcr_mg_g = Decimal('1000') * protein_mg_dL / creatinine_mg_dL
```

Format each output ratio as `f'{ratio:.2f}'` for a plain decimal with exactly two places. Write only `collection_id,uacr_mg_g,upcr_mg_g`; retain the order of complete input rows.
