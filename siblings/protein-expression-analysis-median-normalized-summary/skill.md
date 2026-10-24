## Reference notes

Use **pandas** for the calculations and `.xlsx` output. The task explicitly requires numeric cells, not formulas; calculate in Python rather than following the skill document’s general preference for spreadsheet formulas.

```python
import numpy as np
import pandas as pd

sheets = pd.read_excel("/root/work/raw_intensity.xlsx", sheet_name=None)
data, samples, targets = (sheets[name] for name in ("Data", "Samples", "Targets"))
```

- Inspect sheet shapes and column names briefly before processing. Preserve `Targets` row order. Sample headers may contain multiple underscores: extract the short ID with `header.rsplit("_", 1)[-1]`, **not** `split("_")[1]`. Match that ID to `Samples.Sample_ID` to obtain its condition.
- Convert intensity columns to numbers (`pd.to_numeric(..., errors="coerce")`); treat blanks/non-numeric values and **zero** as missing before taking logs. Intensities are raw linear values: `np.log2(intensities)`.
- Normalize **each sample column** using its median across *all available proteins in Data*, not just targets: `normalized = logged.sub(logged.median(axis=0), axis=1)`. Pandas median and mean skip `NaN` by default.
- For each target, select its normalized values in Control and Treated columns. Counts are non-missing counts; means exclude missing values. Compute `Log2FC = Mean_Treated - Mean_Control`, then `Fold_Change = 2 ** Log2FC` using the **unrounded** difference.
- Round means, Log2FC and Fold_Change independently to four decimals for output; keep counts as integers. If a condition has no observations, its mean and dependent results are undefined—do not substitute zero or infinity.
- Export a DataFrame with the exact requested column order: `summary.to_excel("/root/work/target_summary.xlsx", sheet_name="Summary", index=False)`. This writes the headers in row 1 and numeric results as values. Reopen the file briefly to check the sheet name, headers, target order and a few output cells.
