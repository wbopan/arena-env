# Convert regional revenue using an embedded rate table

The presentation `/root/work/report.pptx` has one slide. The slide contains:

- An embedded Excel workbook (an OLE object stored inside the package under `ppt/embeddings/`). Its first worksheet is a currency rate matrix. Row 1 holds currency codes as column headers from B1 onward. Column A holds currency codes as row labels from A2 downward. The cell at row X and column Y is the rate that converts 1 unit of currency X into currency Y. Some cells are constants. Others are formulas of the form `=1/<cell>`, and you must evaluate them the way Excel would.
- A text box whose first line is `Report currency: <CODE>`. Each following line has the form `<Region>: <amount> <CODE>`. Amounts use comma thousands separators.

For each region, convert its amount into the report currency:

`amount * rate[region currency][report currency]`

Round each converted value to 2 decimals. If a region's currency is already the report currency, its rate is 1.

Write `/root/work/converted.json` with exactly this structure:

```json
{"report_currency": "<CODE>", "converted": {"<Region>": <number>, ...}, "total": <number>}
```

- `converted` must contain every region from the text box, using the exact region names.
- `total` is the sum of the rounded per-region values, rounded to 2 decimals.
- All numbers are JSON numbers, not strings.
