1. Locate `test-supply.xlsx` and the local data files (PWT GEO `rnna`/`rgdpna`, WEO GDP and growth, ECB CFC). Dump each sheet's first ~60 rows of non-empty cells to learn the layout.
2. Write one openpyxl script that puts raw data into the source columns and Excel formulas everywhere else: links, LN, depreciation `=CFC/K`, B3 = AVERAGE of the last 8, K = anchor·Y, TREND to 2041, `Ystar=EXP(lnZ)*K^α`, ΔK=(1-δ)ΔK₋₁+I, K_with.
3. Replace Solver by computing the HP trend in numpy (λ = 100, `solve(I+λD'D, y)`) and writing the values into L6:L27. P5 is the SUMXMY2 + λ·SUMSQ objective.
4. Save to the same `test-supply.xlsx`, run `python recalc.py test-supply.xlsx 60` until there are zero errors, then spot-check key cells with `data_only=True`.
