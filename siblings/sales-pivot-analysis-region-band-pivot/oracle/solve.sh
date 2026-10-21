#!/bin/bash
set -e
cat > /tmp/solve.py <<'EOF'
import pandas as pd
from openpyxl import Workbook
from openpyxl.pivot.table import TableDefinition, Location, PivotField, DataField, RowColField
from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, WorksheetSource, SharedItems

df = pd.read_excel("/root/work/sales.xlsx", sheet_name="Orders")
df["Revenue"] = [round(float(u) * float(p), 2) for u, p in zip(df.Units, df.UnitPrice)]
df["SizeBand"] = ["Small" if u < 10 else ("Medium" if u < 50 else "Large") for u in df.Units]
cols = list(df.columns)

wb = Workbook()
ws = wb.active
ws.title = "SourceData"
ws.append(cols)
for r in df.itertuples(index=False):
    ws.append([v.item() if hasattr(v, "item") else v for v in r])
n = len(df) + 1

pw = wb.create_sheet("Revenue by Region")
cache = CacheDefinition(
    cacheSource=CacheSource(type="worksheet", worksheetSource=WorksheetSource(ref=f"A1:G{n}", sheet="SourceData")),
    cacheFields=[CacheField(name=c, sharedItems=SharedItems()) for c in cols])
pt = TableDefinition(name="RevenueByRegion", cacheId=0, dataCaption="Values",
                     location=Location(ref="A3:E9", firstHeaderRow=1, firstDataRow=2, firstDataCol=1))
for c in cols:
    if c == "Region":
        pt.pivotFields.append(PivotField(axis="axisRow", showAll=False))
    elif c == "SizeBand":
        pt.pivotFields.append(PivotField(axis="axisCol", showAll=False))
    elif c == "Revenue":
        pt.pivotFields.append(PivotField(dataField=True, showAll=False))
    else:
        pt.pivotFields.append(PivotField(showAll=False))
pt.rowFields.append(RowColField(x=cols.index("Region")))
pt.colFields.append(RowColField(x=cols.index("SizeBand")))
pt.dataFields.append(DataField(name="Sum of Revenue", fld=cols.index("Revenue"), subtotal="sum"))
pt.cache = cache
pw._pivots.append(pt)

rt = wb.create_sheet("Region Totals")
rt.append(["Region", "Revenue"])
g = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
for reg, val in g.items():
    rt.append([reg, round(float(val), 2)])
wb.save("/root/work/region_report.xlsx")
EOF
python3 /tmp/solve.py
