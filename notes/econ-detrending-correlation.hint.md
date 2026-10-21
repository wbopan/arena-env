1. Inspect the head/tail of both ERP .xls files (`pd.read_excel(header=None)`, needs xlrd) and CPI.xlsx. Column 0 is the year label, column 1 is Total, and the 2024 quarters sit at the bottom.
2. Build annual PCE and PFI for 1973–2024, with 2024 equal to the mean of the available 2024 quarters. Build annual-average CPI, then compute real = nominal/CPI.
3. Take `np.log`, run `statsmodels hpfilter(x, lamb=100)` (which returns cycle first), then compute `np.corrcoef` of the two cycles.
4. Write `f"{r:.5f}"` to `/root/answer.txt`. Sanity-check 52 points per series and that the file holds a single number.
