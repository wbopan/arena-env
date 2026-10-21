Prepare the node specification for a D3.js (v6) clustered bubble chart of stocks.

Input: `/root/work/data/stock-descriptions.csv` with columns `ticker,name,sector,marketCap,country,website`. ETF rows have sector `ETF` and empty `marketCap`, `country` and `website`.

Write `/root/work/bubbles.json`. It must be a JSON object with two keys.

`legend` is a list of `{"sector": ..., "color": ...}` objects:
- The order is the distinct non-ETF sectors sorted alphabetically, followed by `ETF` last.
- Colors come from d3.schemeCategory10 and are assigned in legend order: #1f77b4, #ff7f0e, #2ca02c, #d62728, #9467bd, #8c564b.

`nodes` has one object per CSV row with these keys:
- `ticker`, `name`, `sector`
- `marketCap`: an integer, or null for ETFs
- `marketCapLabel`
- `radius`
- `color`: the color of the node's sector in the legend
- `tooltip`: false for ETFs, true otherwise

Radius:
- Stocks use `6 + 34 * sqrt(marketCap / maxMarketCap)`, rounded to 2 decimals. The maximum is taken over all stocks.
- ETFs get radius 10.

marketCapLabel is a readable number similar to d3.format(".3s"), but uses B for billions:
- Pick the suffix T (value >= 1e12), B (>= 1e9) or M (>= 1e6) and divide by that unit.
- Show exactly 3 significant digits and keep trailing zeros, e.g. `1.64T`, `12.0B`, `523M`.
- ETFs get an empty string `""`.

Node order:
- Sort by sector, in legend order.
- Within a sector, sort by marketCap descending.
- ETFs are sorted among themselves by ticker ascending.
