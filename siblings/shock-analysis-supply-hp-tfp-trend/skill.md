## Reference notes

Use `pandas` to read the workbook, `numpy` for logs and the HP-filter linear system, and standard-library `json` for output. No Excel file needs to be modified.

```python
import pandas as pd
import numpy as np

macro = pd.read_excel("/root/work/macro_data.xlsx", sheet_name="Macro")
params_df = pd.read_excel("/root/work/macro_data.xlsx", sheet_name="Params")
params = dict(zip(params_df["parameter"], params_df["value"]))
macro = macro.sort_values("year").reset_index(drop=True)
```

Do **not** rely on workbook row order. Convert the relevant columns and parameters to numeric values if needed; `K` and `Y` must be positive before taking natural logs. Compute each annual depreciation ratio *before* averaging the ratios for the specified years (not `sum(CFC)/sum(K)`).

The HP trend for an array `z` of length `n` solves
\[
(I+\lambda D^\mathsf{T}D)\tau=z,
\]
where each row `i` of the `(n-2) × n` second-difference matrix `D` has `[1, -2, 1]` in columns `i:i+3`. A compact construction is:

```python
D = np.diff(np.eye(len(z)), n=2, axis=0)
tau = np.linalg.solve(np.eye(len(z)) + hp_lambda * (D.T @ D), z)
```

Build `z` from natural logs using `np.log`. Take the last trend difference **before rounding**. Round each output float to six decimals when constructing the JSON object; convert years to Python `int` and numeric results to Python `float`. Write with `json.dump(..., allow_nan=False)`. Check the written file has ascending years, the required keys, and finite numbers.
