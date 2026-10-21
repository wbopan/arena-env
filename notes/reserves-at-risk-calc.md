**Goal and output.** Edit the provided workbook and save it to `/root/output/rar_result.xlsx` (run `mkdir -p /root/output` first). The workbook must contain the sheets "Gold price", "Value", "Volume", "Total Reserves" and "Answer". Every computed cell must be an Excel formula, not a value computed in Python. Only the raw gold price data may be hardcoded. The file must have zero formula errors after recalculation.

**1. Locate inputs cheaply.**
- Find the files: `ls -la /root /root/* 2>/dev/null | head -50` and `find / -name "*.xls*" -not -path "*/proc/*" 2>/dev/null | head`.
- Check whether an IMF commodity file (PCPS / "external-data") is already provided locally.
- Dump the layout of each sheet without printing whole files:
```python
from openpyxl import load_workbook
wb=load_workbook(P)
for ws in wb:
    print(ws.title, ws.max_row, ws.max_column)
    for r in ws.iter_rows(min_row=1,max_row=8,values_only=True): print(r[:15])
```
- For the "Answer" sheet, print every non-empty cell with its coordinate. This shows the labels and blanks in rows 1–24, which tell you exactly which cells to fill:
```python
for row in wb['Answer'].iter_rows():
    for c in row:
        if c.value is not None: print(c.coordinate, repr(c.value))
```
- In "Value", "Volume" and "Total Reserves", find the header row and the 2025 column by searching for `2025` or `'2025'`, since years may be text. Note where the country names sit and the units used (e.g. USD millions vs tonnes or troy ounces).

**2. Gold price data (IMF Primary Commodity Prices).**
- If no local copy exists, try downloading. The page https://www.imf.org/en/research/commodity-prices links an Excel file. Use `curl -sL <page> | grep -oi 'href="[^"]*\.xls[x]*"'` to find it. The historical name was `https://www.imf.org/-/media/Files/Research/CommodityPrices/Monthly/external-data.xls`.
- Read `.xls` files with `pd.read_excel(f, header=None)`; this needs `xlrd`. Alternatively convert with `soffice --headless --convert-to xlsx`.
- Gold is series code **PGOLD**, "Gold (UK), 99.5% fine, London afternoon fixing, US$ per troy ounce".
- Dates look like `1990M1` (or similar). Keep the same date format and order as the template's column A in "Gold price".
- Write dates into column A and prices into column B, starting at the template's first data row. Check that the template header is in row 1, and keep the existing headers.

**3. Formulas in "Gold price" (first data row r0, last row rN).**
- C (monthly log return, %): from row r0+1, `=LN(B{r}/B{r-1})*100`. Leave the first row blank, not an error.
- D (3-month volatility): from the third return onward, `=STDEV(C{r-2}:C{r})`. This is the sample standard deviation. Prefer `STDEV` over `STDEV.S` for LibreOffice safety; both are sample sd.
- E (12-month volatility): `=STDEV(C{r-11}:C{r})`, starting once 12 returns exist.
- Do not write formulas that reference blank or text cells. These cause `#DIV/0!` or `#VALUE!`.

**4. Answer, Step 1 (rows 3–6).**
- Latest 3-month volatility: `='Gold price'!D{rN}`.
- Latest 12-month volatility: `='Gold price'!E{rN}`.
- 3-month annualized volatility: `=<3m cell>*SQRT(12)`.
- Fill any fourth blank (for example, annualized 12-month or the latest date) exactly as its label says.

**5. Step 2 (rows 11–13).**
- List every country with a non-empty 2025 value in "Value". Use cross-sheet links such as `=Value!X{row}`, with country names in row 11 and values in row 12.
- Then find countries in "Volume" that have 2025 data and are not in "Value". Add them as further columns.
- For each added country, compute value = volume × average gold price for 2025 Jan–Sep. Write the average as a formula, e.g. `=AVERAGE('Gold price'!B{jan25}:B{sep25})`.
- Watch the units. If volume is in tonnes and value is in USD millions, convert: 1 tonne = 32,150.7466 troy oz, so USD mn = tonnes × 32150.7466 × price / 1e6. Check the header and units text in both sheets and match the "Value" sheet's units.
- Row 13, gold price exposure: reserve value × gold volatility. The near-term hint points to the 3-month annualized volatility from Step 1. Since volatility is in %, use `=B12*$X$vol/100`, with an absolute reference to the Step 1 cell. Follow the row labels if they specify otherwise.

**6. Step 3 (rows 20–24).**
- Rows 20–22: link the country, gold reserve value and volatility from Step 2 (`=B11`, `=B12`, the volatility cell).
- Row 23: look up the 2025 total reserves with `=INDEX('Total Reserves'!$Y:$Y, MATCH(B20,'Total Reserves'!$A:$A,0))`, adjusting columns to the actual layout. Prefer INDEX+MATCH, because XLOOKUP may give `#NAME?` in LibreOffice recalc.
- Before writing, check in Python which countries have a blank 2025 total in "Total Reserves". Omit those countries from the Step 3 table so no `#N/A` or empty values appear. Keep the remaining columns contiguous.
- Row 24, RaR: follow the label. Typically it is gold value × volatility relative to total reserves, e.g. `=B21*B22/100/B23`. If the label asks for a total, use SUM-based formulas over the table instead.
- Country names may differ slightly between sheets (e.g. "China, P.R.: Mainland"). Match the exact strings, and verify with Python before writing.

**7. Write, recalc, verify.**
- Write a single script: `load_workbook(src)`, fill the cells, then `wb.save('/root/output/rar_result.xlsx')`.
- Never load with `data_only=True` and then save; this destroys formulas.
- Recalculate with `python recalc.py /root/output/rar_result.xlsx 60`. Locate the script with `find / -name recalc.py 2>/dev/null`. The JSON must show `"status": "success"`; if it reports errors, fix the listed cells.
- Spot-check the results by reloading with `load_workbook(out, data_only=True)`. Print the Answer cells in rows 3–6, 11–13 and 20–24, plus the last 3 rows of "Gold price".
- Sanity checks:
  - Monthly log returns are roughly −10 to +10.
  - Volatilities are a few %.
  - Annualized volatility = 3-month volatility × 3.464.
  - The date of the latest row matches the latest month in the IMF data.
- Preserve the template's formatting and do not restructure its sheets.
