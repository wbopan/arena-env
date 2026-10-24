## Reference notes

Use `openpyxl` for the Excel files and standard-library `json` for parameters. **The requested output requires numeric values, not Excel formulas**; calculate in Python and write numbers directly. No formula recalculation is needed.

```python
import json
from openpyxl import load_workbook, Workbook

with open('/root/work/params.json') as f:
    params = json.load(f)

src = load_workbook('/root/work/weo.xlsx', read_only=True, data_only=True)
ws = src['WEO_Data']
headers = [cell.value for cell in ws[1]]
col = {name: headers.index(name) for name in headers}  # zero-based tuple indexes
rows = [row for row in ws.iter_rows(min_row=2, values_only=True)
        if row[col['Year']] is not None]

out = Workbook()
sheet = out.active
sheet.title = 'Impact'
sheet.append(['Year', 'Deflator', 'Real_GDP', 'Investment_GEL',
              'Real_Investment', 'GDP_Impact', 'Impact_pct'])
# sheet.append([int(year), deflator, real_gdp, investment_gel,
#               real_investment, gdp_impact, impact_pct])
out.save('/root/work/shock_impact.xlsx')
```

- Identify **L** as the last year with *both* nominal GDP and deflator present; blank projection cells are `None`. Map records by integer year rather than assuming worksheet rows have no gaps.
- Deflator growth is the **arithmetic mean of four separate rates** for years `L-3` through `L`. Those rates require deflators for `L-4` through `L`. For later years, compound the deflator one year at a time.
- Anchor real GDP at `L` using `Nominal_L / D_L * 100`; compound subsequent real GDP using each year’s `Real GDP growth (%) / 100`. If the project starts after `L+1`, still project through every intervening year.
- `allocation_weights` correspond in order to consecutive years beginning at `start_year`; divide each by their **sum**. USD billions × GEL/USD yields GEL billions. Convert nominal investment to 2019-price GEL billions with `/ D_t * 100`, then apply `(1 - import_content_share) * demand_multiplier`. `Impact_pct` is the resulting impact divided by that year’s real GDP, **times 100**.
- Write one row per project year in ascending order. Keep year as an integer and all other outputs as unrounded Python numbers (or retain at least six decimals); don’t write `None`, strings, or formulas to data cells. Reload the saved workbook with `data_only=True` for a quick check of headers, row count, and numeric cell types.
