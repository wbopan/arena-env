**Goal and output.** Fill the provided template workbook and save it as `test_demand.xlsx` in the task's working or output directory. Use the same directory as the template unless the task files say otherwise. Every calculated cell must hold an Excel formula string, not a value computed in Python. Use Python and openpyxl only as a typing tool to write the formulas. The only hardcoded entries allowed are:
- raw source data (WEO figures and the copied SUPPLY/USE sheets);
- the stated assumptions: FX 2.746, multiplier 0.8 or 1, import share 0.5 in Scenario 3, and the bell-shape weights.

Keep the template's sheet names, layout and styles. Never open the file with `data_only=True` and then save it, because that permanently replaces formulas with values.

**Inspect cheaply first** (one command each, never print whole files):
- `ls -la; find / -name "*.xlsx" -newer /etc/hostname 2>/dev/null | head` to locate the template and any pre-downloaded WEO or Geostat files (csv/xlsx). If there is no internet, the data must come from those local files.
- Dump the template structure without values:
  `python -c "import openpyxl;wb=openpyxl.load_workbook('T.xlsx');[print(ws.title,ws.dimensions) for ws in wb]"`
- Print only labels and existing formulas of each sheet:
  `for r in ws.iter_rows(max_row=60,max_col=12): print([ (c.coordinate,c.value) for c in r if c.value is not None])`
  Do this for "WEO_Data", "SUT Calc" and "NA". From this, identify the year columns, the row labels (e.g. real GDP growth, nominal GDP, GDP deflator), the headers of SUT Calc columns C–H, and the labels of NA D30–D33.
- For the Geostat SUT file, list the sheet names and find the exact "SUPPLY" and "USE" sheets (38×38 products). Locate the rows and columns for:
  - in SUPPLY: imports (c.i.f./total imports) and total supply;
  - in USE: gross fixed capital formation.
  Use `print` with `max_row`/`max_col` limits only.

**STEP 1 – WEO_Data.**
1. Enter the WEO values (Georgia) in the rows the template expects: real GDP growth, nominal GDP (GEL), GDP deflator, etc., for the available years. Add a source note beside the table.
2. Real growth for 2028–2043 is the 2027 value, written as a reference, e.g. `=$X$r` pointing to the 2027 cell, or `=prev`.
3. Deflator growth anchor is the average of the last 4 actual or observed deflator growth rates, written as a formula: `=AVERAGE(...)` over the growth cells, or e.g. `=(D_t/D_{t-4})^(1/4)-1` if growth cells don't exist. Follow the template's labels.
4. Extended deflator: `=prev*(1+anchor)`.
5. Real GDP: `=prev*(1+g)`.
6. Nominal GDP: `=real*deflator/100`, or prev nominal × (1+g)(1+π), consistent with how the template defines its rows.

**STEP 1 – SUT.**
1. Copy the SUPPLY and USE sheets cell by cell into the workbook with the exact original sheet names. Use `wb.create_sheet(name)` and loop `ws2.cell(r,c).value = src.value`; copying values is fine for raw data.
2. In "SUT Calc", columns C–E link into the copied sheets, e.g. `='SUPPLY'!X12`, `='USE'!Y12`, per product row.
3. Columns F–H are calculations. The usual logic:
   - product import share = imports / total supply;
   - imported GFCF = GFCF × that share.
4. Estimated import content of investment: C46 = `SUM(imported GFCF)/SUM(GFCF)`, i.e. a GFCF-weighted import share.
5. Match the template's column headers exactly. If they define something different, follow the headers.
6. Guard divisions with `=IF(den=0,0,num/den)` to avoid `#DIV/0!`.

**STEP 2 – NA sheet (Scenario 1).**
- Column C (and J) link to WEO_Data, e.g. `=WEO_Data!E5`, matching years by row.
- Assumptions D30–D33 (check the labels; likely):
  - FX = 2.746;
  - multiplier = 0.8;
  - import content = `='SUT Calc'!C46`;
  - total investment = 6.5 (bn USD) or 6500 (mn), matching the units of the GDP column.
- Bell-shaped allocation over the 8 years 2026–2033: symmetric weights peaking in the middle that sum to 1, e.g. 5%,10%,15%,20%,20%,15%,10%,5%. Put the weights in cells. A sum check cell `=SUM(...)` should equal 1.
- Typical row chain per year (use $-anchored assumption references):
  1. investment USD = total × weight;
  2. nominal GEL = USD × FX, with units converted to match GDP;
  3. real investment = nominal / (deflator/100), since the GDP deflator serves as the investment deflator;
  4. domestic component = real × (1 − import share);
  5. GDP impact = domestic × multiplier;
  6. impact % of GDP = impact / baseline real (or nominal-consistent) GDP;
  7. shocked GDP = baseline + impact;
  8. shocked growth = shocked_t / shocked_{t−1} − 1, against baseline growth.
- Years outside 2026–2033 have zero investment and zero impact, using the same formula with weight 0. Do not leave blanks that break the formula chain.

**STEP 3 – Scenarios.**
1. Copy Scenario 1's block below it twice: same rows and columns, with a scenario title. Write the formulas in a loop with a row offset; don't paste values.
2. Each block gets its own assumption cells:
   - Scenario 2: multiplier = 1, with the other assumptions linked to Scenario 1's cells.
   - Scenario 3: import share = 0.5, multiplier 0.8.
3. Block formulas must reference their own block's assumption cells.

**Formatting conventions (only if the template has none).** Blue = hardcoded inputs, black = formulas, green = cross-sheet links. Years go as text. Percentages use 0.0%.

**Script plan.**
1. Write a single `build.py`:
   - load the template with openpyxl (formulas preserved);
   - add the SUPPLY/USE sheets;
   - write WEO data and formulas;
   - fill SUT Calc, NA and the 3 scenarios;
   - `wb.save('test_demand.xlsx')`.
2. Run `python recalc.py test_demand.xlsx 60` (find recalc.py with `find / -name recalc.py`). It must report `status: success` and 0 errors. Fix any `#REF!`, `#NAME?` or `#DIV/0!` it lists.
3. Verify by reading a few computed cells with a separate `load_workbook(...,data_only=True)` (read only, no save):
   - C46 is between 0 and 1;
   - weights sum to 1;
   - investment rows sum to 6.5bn × FX;
   - Scenario 2 impact = Scenario 1 × 1.25;
   - extended WEO years show no blanks.
4. Confirm that formula cells start with "=" by loading without `data_only` and spot-checking.
