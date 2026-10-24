## Reference notes

Use `openpyxl` to read the workbook and Python’s `json` module to write the result. Excel rows and columns are **1-indexed**. Row 3 contains headers; product data begins at row 4. Match columns by their header text, not by guessed column letters.

```python
from openpyxl import load_workbook

wb = load_workbook("/root/work/sut.xlsx", read_only=True, data_only=True)
supply, use = wb["SUPPLY"], wb["USE"]

def columns(ws):
    return {cell.value: cell.column for cell in ws[3] if cell.value is not None}
```

`data_only=True` reads cached results if cells contain formulas; `openpyxl` does not calculate formulas. Inspect the few relevant headers and sample rows if cached values are missing.

Build separate mappings keyed by the product code in column A, then join **by code**, not row position. Exclude the `TOTAL` row; a blank GFCF cell (`None`) means zero. Check that product-code sets agree and that supply denominators and aggregate GFCF are nonzero before dividing.

Compute each ratio as `Imports CIF / Total supply at purchasers prices`, and each contribution as `GFCF * ratio`. Sum unrounded contributions and GFCF before calculating the share; round only the final JSON values. `max(contributions, key=contributions.get)` selects the largest contributor. `json.dump(...)` writes decimal-valued Python numbers as JSON numbers, not percentage strings.
