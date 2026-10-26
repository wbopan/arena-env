## Reference notes

- Use Python’s standard-library `csv` module. `csv.DictReader` preserves input row order and lets you access the named columns; `csv.DictWriter(..., fieldnames=[...])` fixes output column order. Open files with `newline=''`. A comma-decimal numeric cell must be quoted in the input CSV so the CSV reader treats it as one field.
- Keep `patient_id` as text. For each numeric cell, strip surrounding whitespace, replace its decimal comma with `.`, then parse it. `float()` accepts scientific notation; `decimal.Decimal` also accepts it and avoids binary floating-point artifacts.
- **Use the explicit unit labels**, not value ranges, to select conversions. Do not filter complete rows, clamp values, or discard discordant pairs.

```python
from decimal import Decimal

def number(cell):
    return Decimal(cell.strip().replace(',', '.'))

def two_places(value):
    return format(value, '.2f')
```

For each row, calculate with unrounded values:

- `IFCC_mmol_mol` → NGSP percent: `IFCC / 10.929 + 2.15`; `NGSP_percent` stays unchanged.
- eAG (mg/dL): `28.7 * NGSP_percent - 46.7`.
- Measured glucose: multiply by `18.02` only for `mmol/L`; `mg/dL` stays unchanged.
- Gap (mg/dL): **converted measured glucose minus eAG**.

If using `Decimal`, construct constants from strings (for example, `Decimal('18.02')`). Format only when writing the four measurement columns, with exactly two decimal places; leave negative gaps signed. Write the header exactly as requested and one output row per input row.
