## Reference notes

Use **openpyxl** for reading the workbook, writing numeric cells, and adding a real Excel pivot table. No PDF guidance applies.

```python
from collections import defaultdict
from openpyxl import Workbook, load_workbook
from openpyxl.pivot.table import (
    TableDefinition, Location, PivotField, DataField, RowColField,
)
from openpyxl.pivot.cache import (
    CacheDefinition, CacheField, CacheSource, WorksheetSource, SharedItems,
)

src = load_workbook(input_path, data_only=True)["Orders"]
headers = [cell.value for cell in src[1]]
for values in src.iter_rows(min_row=2, values_only=True):
    row = dict(zip(headers, values))
    # Preserve order; calculate Revenue and SizeBand; append numeric values.
```

- `Revenue = round(Units * UnitPrice, 2)`. Bands: `< 10` Small; `10–49` Medium; `>= 50` Large. Append Python numbers, not formatted strings. For the static totals, accumulate revenue by region, round totals to two decimals, then sort descending.
- `Workbook()` starts with one sheet: rename `wb.active`, then use `wb.create_sheet(...)` for the other two. `ws.append([...])` writes a row. The pivot source reference must include the header and every data row, through column G.

Pivot API pattern (derive field indexes from the **SourceData** header order):

```python
cache = CacheDefinition(
    cacheSource=CacheSource(
        type="worksheet",
        worksheetSource=WorksheetSource(
            ref=source_ref, sheet="SourceData"
        ),
    ),
    cacheFields=[
        CacheField(
            name=name,
            sharedItems=SharedItems(count=unique_count[name])
            if name in categorical_names else SharedItems(),
        )
        for name in source_headers
    ],
)

pivot = TableDefinition(
    name="RevenueByRegion",
    cacheId=0,
    dataCaption="Values",
    location=Location(
        ref=pivot_location,
        firstHeaderRow=1, firstDataRow=1, firstDataCol=1,
    ),
)
pivot.pivotFields = [PivotField(showAll=False) for _ in source_headers]
pivot.pivotFields[row_index] = PivotField(axis="axisRow", showAll=False)
pivot.pivotFields[col_index] = PivotField(axis="axisCol", showAll=False)
pivot.pivotFields[value_index] = PivotField(dataField=True, showAll=False)
pivot.rowFields.append(RowColField(x=row_index))
pivot.colFields.append(RowColField(x=col_index))
pivot.dataFields.append(
    DataField(name="Sum of Revenue", fld=value_index, subtotal="sum")
)
pivot.cache = cache
pivot_ws._pivots.append(pivot)
wb.save(output_path)
```

Field indexes are zero-based and must match `cacheFields`/source-column order. Use `cacheId=0` as specified by the openpyxl skill; other IDs can cause a read-back `KeyError`. `Location.ref` describes the pivot’s placement, not its source range. Pivot values are populated when Excel/LibreOffice opens and calculates the workbook; openpyxl creates the pivot definition but does not calculate its displayed values.
