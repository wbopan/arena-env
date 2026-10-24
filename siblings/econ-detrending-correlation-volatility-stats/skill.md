## Reference notes

Use `openpyxl` for the workbooks, `pandas` for the dated CPI file, and `numpy` for the HP filter and statistics. The HP filter can be computed directly; no additional time-series package is needed.

- Load each workbook with `openpyxl.load_workbook(path, read_only=True, data_only=True)` and select `wb["Table"]`. Iterate `sheet.iter_rows(values_only=True)`: column A is `row[0]`, column B is `row[1]`. Skip title, header, and notes rows by recognizing labels rather than assuming a fixed row number. Annual labels may be numeric Excel cells; quarterly labels have the form `YYYY: II`. Do not treat a quarterly row or source footnote as an annual observation.
- Read CPI with `pd.read_csv(path, parse_dates=["observation_date"])`. Group by `df["observation_date"].dt.year` and take the mean of `CPIAUCSL`. This naturally uses only available months for a partial year.
- Keep both nominal series and CPI aligned in ascending year order. Use annual nominal rows where present; for a year without an annual row, average its available quarterly column-B values. Compute `real = nominal / annual_cpi * 100`, then take `np.log(real)` **before** filtering.

For an annual log series `y`, λ = 100. The following implements the stated HP objective; `D @ trend` contains its second differences:

```python
import numpy as np

def hp_cycle(y):
    y = np.asarray(y, dtype=float)
    n = len(y)
    D = np.diff(np.eye(n), n=2, axis=0)
    trend = np.linalg.solve(np.eye(n) + 100 * D.T @ D, y)
    return y - trend
```

Apply it separately to the two complete, year-aligned real series. Use `np.std(cycle, ddof=1) * 100` for each percent volatility and `np.corrcoef(cycle_pce, cycle_pfi)[0, 1]` for Pearson correlation. Divide the **unrounded** percent volatilities for relative volatility; round floats only when assembling the JSON object. Write it with the standard-library `json` module, then reopen the file to check its keys and values.
