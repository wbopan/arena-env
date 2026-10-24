## Reference notes

Use Python’s standard-library `csv`, `json`, and `math`; this task produces a JSON node specification, not a rendered D3 chart. No D3 installation is needed.

```python
import csv, json, math

with open(input_path, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
```

`DictReader` returns strings: convert stock `marketCap` values with `int(...)`; treat an ETF’s empty field as `None`, never zero. Compute `maxMarketCap` over stocks only.

- Legend sectors: `sorted({r["sector"] for r in rows if r["sector"] != "ETF"}) + ["ETF"]`.
- Assign colors **by legend position**, using the supplied six `schemeCategory10` hex values in order. Use that same sector-to-color mapping for nodes.
- Stock radius: `round(6 + 34 * math.sqrt(cap / max_cap), 2)`; ETF radius: `10`.
- For a stock label, choose the suffix from the **original integer** (`T` ≥ `10**12`, else `B` ≥ `10**9`, else `M` ≥ `10**6`), divide by its unit, then format to **three significant digits with trailing zeros**. For scaled values from 1 to under 1000, the number of decimal places is `max(0, 2 - math.floor(math.log10(scaled)))`; fixed-point formatting (`f"{scaled:.{places}f}"`) retains zeros. ETF label: `""`.
- Sort nodes by legend sector index, then stock market cap descending; sort ETFs by ticker ascending. An explicit sort key can use `(sector_index[sector], -cap, ticker)` for stocks and `(sector_index["ETF"], 0, ticker)` for ETFs.
- Write an object containing `legend` and `nodes` with `json.dump(...)`. Python `None`, `True`, and `False` become JSON `null`, `true`, and `false`. Use `newline=""` when reading CSV to handle quoted fields correctly.
