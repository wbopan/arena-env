## Reference notes

Use `pandas` for the TSVs and CSV output. The related 13F search scripts can identify a CUSIP, but direct TSV processing is better here because the requested position and portfolio definitions require different line filters.

```python
import pandas as pd
from pathlib import Path

root = Path("/root/work/2025-q3")
cover = pd.read_csv(root / "COVERPAGE.tsv", sep="\t", dtype=str, keep_default_na=False)
info = pd.read_csv(root / "INFOTABLE.tsv", sep="\t", dtype=str, keep_default_na=False)
info["VALUE"] = pd.to_numeric(info["VALUE"])
```

Keep accession numbers and CUSIPs as **strings**. `keep_default_na=False` preserves empty `PUTCALL` cells as `""`; if using pandas’ default NA handling instead, account for missing values explicitly.

- Find the target CUSIP from `NAMEOFISSUER.str.contains("palantir", case=False, na=False)`; confirm that the matching rows identify one CUSIP.
- **Position:** for that CUSIP, include only `SSHPRNAMTTYPE == "SH"` and empty `PUTCALL`; sum `VALUE` by `ACCESSION_NUMBER`.
- **Portfolio:** sum `VALUE` by `ACCESSION_NUMBER` over the *entire* information table, without the position filters.
- Join those sums to `COVERPAGE` on `ACCESSION_NUMBER`. Retain positive positions; sort by position descending, then accession number ascending; take five.
- Compute `100 * position / portfolio`, round to two decimal places, and write with `to_csv("/root/work/top_holders.csv", index=False)`. Select and order the five requested output columns explicitly. Formatting percentages with `f"{pct:.2f}"` ensures two digits after the decimal point.
