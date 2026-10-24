## Reference notes

Use Python’s standard-library `csv` and `json` modules to work directly from the supplied TSVs. The skill scripts provide summary reports, but exact-name matching, stock-line filtering, and CUSIP-level aggregation are needed here; fuzzy search is unnecessary.

```python
import csv

def rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t")
```

- Find the filer **separately in each quarter’s** `COVERPAGE.tsv` using `FILINGMANAGER_NAME.strip().casefold()`. Retain each quarter’s `ACCESSION_NUMBER` as a string; the accessions differ.
- In each `INFOTABLE.tsv`, keep only rows for that quarter’s accession where `SSHPRNAMTTYPE.strip().upper() == "SH"` and `PUTCALL.strip() == ""`. This excludes options and principal-amount lines.
- Treat `CUSIP` as a string throughout so leading zeros survive. Sum `int(VALUE)` by CUSIP within each filing before comparing quarters; do not rank individual holding lines.
- Total stock value is the sum of those aggregated position values. Compare the two CUSIP sets for new, exited, and common positions. For common positions, calculate `q3_value - q2_value` and retain only positive changes.
- Sort by descending relevant value or increase, then ascending CUSIP to break ties. For example: `sorted(cusips, key=lambda c: (-values[c], c))`.
- Write integer totals and CUSIP-string lists with `json.dump(...)` to `/root/work/changes.json`. After running the script, read the JSON back and inspect its keys, types, and list lengths.
