1. Inspect the Data orientation/headers and Task rows 9–10, 23–27 and 31–41 with small openpyxl prints. Check whether the Task sample names are suffixes of the prefixed Data names, and which columns are Control vs Treated.
2. Using openpyxl (no data_only), write INDEX/MATCH formulas into Task!C11:L20, with `"*"&name` wildcard matching if the names are partial.
3. Write AVERAGE/STDEV formulas over each group's cells into B24:K27 (one protein per column, row order per labels), then `=Treated−Control` in C32:C41 and `=2^C` in D32:D41.
4. Save to the same file, run `python recalc.py protein_expression.xlsx 60` until there are 0 errors, and spot-check one protein against pandas.
