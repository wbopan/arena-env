Render a static multi-series stock line chart as an SVG file. Compute the coordinates exactly as D3.js (v6) time and linear scales would.

Inputs: `/root/work/data/indiv-stock/*.csv`
- There is one file per ticker; the ticker is the file name without `.csv`.
- Columns are `Date,Open,High,Low,Close,Volume`, with dates in ISO `YYYY-MM-DD` format.
- Rows are not in date order, and the files cover different date ranges.

Chart:
- The root `<svg>` element must have `width="600" height="300"`.
- x is a time scale. Its domain is [earliest date, latest date] over all files and its range is [50, 580]. Position is linear in calendar days.
- y is a linear scale on Close. Its domain is [min Close, max Close] over all files and its range is [270, 20] (inverted).

Write `/root/work/chart.svg`. For each ticker it must contain:
- A line: `<path class="line" data-ticker="TICKER" d="...">`.
  - `d` has the form `M x,y L x,y L x,y ...`, with one point per CSV row.
  - Points are ordered by date ascending.
  - Coordinates are rounded to 2 decimals.
  - Paths should have `fill="none"` and a stroke color.
- A label: `<text class="label" data-ticker="TICKER" x=".." y="..">TICKER</text>`.
  - x is the last point's x + 5, and y is the last point's y.
  - Both are rounded to 2 decimals.

Other decorative elements, such as axes or a title, are allowed, but they must not use the classes `line` or `label`.
