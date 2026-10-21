**Inputs and libraries**
- `/root/population.pdf`: read it with `pdfplumber`, not by printing the file. Loop over **all** pages with `page.extract_tables()`.
  - Only the first page may carry the header row.
  - On continuation pages, the first row is data. It may also be a repeated header; skip rows equal to the header.
  - Strip whitespace from cells.
  - Remove thousands separators (`"12,345"` → `12345`) before converting to int or float.
  - Drop empty or None rows.
- `/root/income.xlsx`: read it with `pd.read_excel` and check every sheet with `sheet_name=None`.
- Output: build it with `openpyxl`, which has a pivot API (`openpyxl.pivot.table` and `openpyxl.pivot.cache`).

**Cheap inspection (do not dump whole files)**
```bash
python3 -c "import pdfplumber;p=pdfplumber.open('/root/population.pdf');print(len(p.pages));t=p.pages[0].extract_tables();print(len(t),t[0][:3]);print(p.pages[-1].extract_tables()[0][:2])"
python3 -c "import pandas as pd;d=pd.read_excel('/root/income.xlsx',sheet_name=None);[print(k,v.shape,list(v.columns),v.head(2).to_dict('records')) for k,v in d.items()]"
```
- Find the join key, most likely an SA2 code or name column present in both files.
- Find where STATE, POPULATION_2023, EARNERS and MEDIAN_INCOME live.
- Keep the original column names, uppercase as given.

**Data preparation**
- Build the population DataFrame from all PDF rows and convert numeric columns with `pd.to_numeric`.
- Merge it with the income data on the key.
  - Make key dtypes match, e.g. both as str stripped, or both int.
  - Use an inner join unless the inspection suggests otherwise.
  - Print row counts before and after the merge and check that nothing is unexpectedly lost or duplicated.
  - Drop rows with missing MEDIAN_INCOME/EARNERS only if necessary.
- Quarter, computed across all regions:
  `df['Quarter'] = pd.qcut(df['MEDIAN_INCOME'], 4, labels=['Q1','Q2','Q3','Q4']).astype(str)`
- Total: `df['Total'] = df['EARNERS'] * df['MEDIAN_INCOME']`
- Write native Python numbers, not numpy types, and not strings for numeric columns. Use `.tolist()` or `.item()`, or convert per cell.

**Workbook layout** (exact sheet names)
1. "SourceData": header row 1, then the merged data plus `Quarter` and `Total`.
   - Optionally wrap it in an Excel table:
     `from openpyxl.worksheet.table import Table; ws.add_table(Table(displayName="SourceData", ref=f"A1:{last_col}{n+1}"))`
     The `displayName` must have no spaces.
2. "Population by State": rows STATE, values sum of POPULATION_2023.
3. "Earners by State": rows STATE, values sum of EARNERS.
4. "Regions by State": rows STATE, values count. Count any field, e.g. the SA2 code or name column.
5. "State Income Quartile": rows STATE, columns Quarter, values sum of EARNERS.

**Pivot recipe (from the skill)**
- **Every pivot uses `cacheId=0`.** Any other value gives a `KeyError` when the file is read back.
- `cacheFields` must list **every** SourceData column in order.
- `pivotFields` must have one entry per column, in the same order.

```python
from openpyxl.pivot.table import TableDefinition, Location, PivotField, DataField, RowColField
from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, WorksheetSource, SharedItems
from openpyxl.utils import get_column_letter
cols=list(df.columns); n=len(df); ref=f"A1:{get_column_letter(len(cols))}{n+1}"
def make_pivot(ws,name,row_col,data_col,agg,col_col=None):
    cache=CacheDefinition(cacheSource=CacheSource(type="worksheet",
        worksheetSource=WorksheetSource(ref=ref,sheet="SourceData")),
        cacheFields=[CacheField(name=c,sharedItems=SharedItems(count=int(df[c].nunique()) if df[c].dtype==object else None)) for c in cols])
    p=TableDefinition(name=name,cacheId=0,dataCaption="Values",
        location=Location(ref="A3:F20",firstHeaderRow=1,firstDataRow=1,firstDataCol=1))
    r,d=cols.index(row_col),cols.index(data_col); c=cols.index(col_col) if col_col else None
    for i in range(len(cols)):
        if i==r: p.pivotFields.append(PivotField(axis="axisRow",showAll=False))
        elif i==c: p.pivotFields.append(PivotField(axis="axisCol",showAll=False))
        elif i==d: p.pivotFields.append(PivotField(dataField=True,showAll=False))
        else: p.pivotFields.append(PivotField(showAll=False))
    p.rowFields.append(RowColField(x=r))
    if c is not None: p.colFields.append(RowColField(x=c))
    p.dataFields.append(DataField(name=f"{'Sum' if agg=='sum' else 'Count'} of {data_col}",fld=d,subtotal=agg))
    p.cache=cache; ws._pivots.append(p)
```

Calls:
- `make_pivot(wb.create_sheet("Population by State"),"PopulationByState","STATE","POPULATION_2023","sum")`
- Same for EARNERS ("Earners by State").
- Count ("Regions by State").
- `col_col="Quarter"` with EARNERS sum ("State Income Quartile").
- Pivot names must be unique and have no spaces.
- If STATE is also the data field (as in some count setups), avoid it: choose a different column to count.

Rename the default sheet to "SourceData" with `ws = wb.active; ws.title = "SourceData"`. Save to **`/root/demographic_analysis.xlsx`**.

Pivot values are computed by Excel or LibreOffice when the file is opened. The definitions are what matter. Do not put other content in the pivot location range.

**Verification (one short script)**
- `load_workbook('/root/demographic_analysis.xlsx')` succeeds.
- `wb.sheetnames` contains all 5 names.
- For each pivot sheet: `len(ws._pivots)==1`, and the row field index points to STATE.
- Data field subtotal and fld are correct.
- The quartile pivot has a colField pointing to Quarter.
- `pd.read_excel(..., 'SourceData')`:
  - Has Quarter values exactly {Q1, Q2, Q3, Q4}, roughly equal counts.
  - Total equals EARNERS*MEDIAN_INCOME.
  - Row count matches the merge.
  - Numeric dtypes are numeric.
- Print `df.groupby('STATE')[['POPULATION_2023','EARNERS']].sum()` as a sanity check.

**Pitfalls**
- Missing PDF continuation pages.
- Comma-formatted numbers left as strings.
- Join key dtype mismatch, which silently drops rows.
- Quartiles computed per state instead of across all regions.
- cacheId ≠ 0.
- pivotFields count not equal to the column count.
- Sheet-name typos.
