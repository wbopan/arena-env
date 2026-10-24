## Reference notes

Use Python’s standard library (`csv`, `glob`, `datetime`, `pathlib`, `xml.etree.ElementTree`); D3 is not needed to generate this static SVG.

- Discover `*.csv` files; use each file’s stem as its ticker. Read with `csv.DictReader`, parse `Date` using `date.fromisoformat(row["Date"])`, and convert `Close` to `float`. Sort each ticker’s rows by date before making its path.
- Compute **both domains across all files**, not separately for each ticker. Dates in `YYYY-MM-DD` form are calendar dates; `date.toordinal()` gives a convenient day count, unaffected by local timezone or daylight-saving changes.
- D3-style linear interpolation for these specified ranges is:

  ```python
  x = 50 + (day - first_day) / (last_day - first_day) * (580 - 50)
  y = 270 + (close - min_close) / (max_close - min_close) * (20 - 270)
  ```

  If a domain has identical endpoints, a D3 continuous scale maps it to the range midpoint instead of dividing by zero.

- Format **each resulting coordinate** to two decimal places (for example, `f"{x:.2f}"`). Build path data in sorted-date order as `M x,y L x,y ...`; the label position uses the final point’s **unrounded** x plus 5 and its y, then formats both to two decimals.
- `xml.etree.ElementTree` can create the root with `width="600"`, `height="300"`, and `xmlns="http://www.w3.org/2000/svg"`; use subelements for paths and text so ticker values are XML-escaped. Give paths `fill="none"` and a deterministic stroke color. Only the requested marks should receive the `line` and `label` classes.
- Short workflow: inspect filenames and a header/sample cheaply; write one script to load, sort, scale, and serialize; run it; inspect the resulting SVG’s root and a path/label sample.
