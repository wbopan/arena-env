**Goal.** Fill the provided workbook `test-supply.xlsx` (find it with `find / -name "test-supply.xlsx" 2>/dev/null`) and save it under the same name and path. Every calculated cell must be an Excel formula string written with openpyxl. Only raw source data may be typed in as numbers. Keep all template text, formulas and formatting.

**Tools.**
- Use openpyxl `load_workbook(path)` to edit. Never save a workbook opened with `data_only=True`, because that deletes every formula.
- After saving, run `python recalc.py test-supply.xlsx 60`. It recalculates in LibreOffice and returns JSON. You need `"status": "success"` and zero errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?).
- Read back values with a separate `load_workbook(path, data_only=True)` and only print a few cells.

**Inputs: inspect cheaply first.**
1. `ls` the task directory for data files: PWT (`pwt*.xlsx`), WEO, ECB CFC CSV, and any Investment data. Online access or Playwright may not exist, so prefer local files.
2. Print the template layout without printing the whole file, using a one-liner per sheet:
   `for r in ws.iter_rows(min_row=1,max_row=60,max_col=16): print([c.coordinate+':'+str(c.value) for c in r if c.value is not None])`
   Sheets: PWT, WEO_Data, CFC data, Production, Investment. Note the headers, year rows, units, and which cells already hold formulas or parameters (capital share α, λ, USD/GEL rate).
3. PWT data: read with pandas `read_excel(..., sheet_name='Data')` and filter `countrycode=='GEO'`. Check the `Legend` sheet for variable meanings.
   - Capital stock at constant national prices = `rnna`.
   - Real GDP at constant national prices = `rgdpna`.
   - Other variables: `labsh` (labour share), `delta` (depreciation).
   - Match what the column B/C headers ask for, over the years the sheet lists.
4. WEO data: Georgia real GDP level (constant prices, national currency) and real GDP growth for 2000–2027. ECB data: annual consumption of fixed capital for Georgia. Check units (millions vs billions) and make them consistent with K.

**Formulas to build (adapt row and column numbers to the template).**

*WEO_Data*
- Paste actual values for 2000–2027.
- Growth for 2028–2043 is a link to the cell above or to the 2027 cell, e.g. `=C29`.
- Level: `=B(prev)*(1+C(row)/100)`. Drop the /100 if growth is stored as a decimal.

*CFC data*
- Column C = CFC values.
- Column D = link to PWT capital, e.g. `=PWT!C10`.
- Depreciation rate = `=C/D`. If the template defines it with lagged capital, follow the template.

*Production!B3*
- `=AVERAGE('CFC data'!E{last8 rows})`, i.e. the most recent 8 years that have data.

*HP section (rows 6–27)*
- D = K link and E = Y link from other sheets.
- LnK `=LN(D6)` and LnY `=LN(E6)`.
- LnZ (column F, often linked again in K) = `=LnY - alpha*LnK`, with α as an absolute ref (e.g. `$B$2`), i.e. ln Z = ln Y − α ln K.
- L6:L27 (LnZ_HP) starts as a placeholder `=K6`.
- Second difference (M8:M27): `=L8-2*L7+L6`.
- Column N check: `=K6-L6` (equals 0 at the start).
- Objective P5: `=SUMXMY2(K6:K27,L6:L27)+lambda*SUMSQ(M8:M27)`. Use λ = 100 for annual data unless the sheet gives one.

*Replacing Solver.* There is no Solver in LibreOffice headless. Solver's output is constants in the changing cells anyway, so compute the minimiser in Python and write the numbers into L6:L27 (all other columns stay formulas):
```python
import numpy as np
y=np.array(lnZ); n=len(y); D=np.diff(np.eye(n),2,axis=0)
tau=np.linalg.solve(np.eye(n)+lam*D.T@D, y)
```
Here `lnZ` must be computed in Python from the same data the formulas use. Then check that P5 after recalculation is lower than its placeholder value.

*Production function table (rows 36–57, extending to 2041 or 2043 per the template)*
- K links PWT up to 2023. Y links up to 2025, then WEO_Data extended levels.
- K/Y = `=K/Y` for 2002–2023.
- Anchor = `=AVERAGE(` the last 9 K/Y values `)`.
- For years after 2023: K = `=$anchor*Y`.
- G36:G57 = links to L6:L27.
- Trend to 2041: `=TREND($G$36:$G$57,$A$36:$A$57,A58)`, where column A holds the years. Lock the ranges.
- Ystar_base = `=EXP(G)*K^alpha`. Follow the template's exact definition; if labour is included, use `EXP(G)*K^α*L^(1-α)`.
- Column I = Investment sheet links. Convert USD to national currency or units if the sheet indicates it.
- ΔK accumulation: `=(1-$B$3)*ΔK_prev + I`, starting from 0 before 2026.
- K_with = `=K_base + ΔK`.
- Ystar_with = `=EXP(G)*K_with^alpha`.
- Remaining columns (e.g. gap = Ystar_with − Ystar_base and % difference) are simple formulas. Fill them across all projection rows consistently.

**Pitfalls**
- Wrong row offsets: check 2–3 links per sheet before filling down.
- Mismatched units between CFC and K, or between Y and investment.
- Growth stored as a percent versus a decimal.
- Using relative refs where B3 or α must be absolute.
- Writing formulas into cells already holding template formulas.
- Empty cells that cause #DIV/0!.

**Plan (about 10 commands)**
1. Find the files.
2. Dump the template structure per sheet, limited to about 60 rows.
3. Inspect the source data heads.
4. Write one script, `fill.py`: load the data, write raw values, write all formulas, compute the HP trend into L6:L27, then save.
5. Run `recalc.py` and fix any reported errors.
6. Run a data_only spot-check: B3, P5, N column ≈ 0 before HP (and after HP, the residual is small), K/Y anchor, a few Ystar_base and Ystar_with values for 2026–2041, and Ystar_with > Ystar_base from 2026.
