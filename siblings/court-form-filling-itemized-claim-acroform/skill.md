## Reference notes

Use **pypdf** to preserve and fill the existing AcroForm, rather than drawing text onto the page. Inspect the small inputs first: `case.json` for its actual key names and boolean representation, the CSV header and statuses, and the PDF fields.

```python
import csv, json, re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader, PdfWriter

root = Path("/root/work")
case = json.loads((root / "case.json").read_text())
with (root / "expenses.csv").open(newline="") as f:
    rows = list(csv.DictReader(f))

reader = PdfReader(root / "claim_form_blank.pdf")
print(reader.get_fields())  # field names, types (/FT), current values (/V)
```

For each checkbox, inspect its **on export value**; do not assume `/Yes`. Its widget’s normal appearance (`/AP` → `/N`) has state names, typically `/Off` plus one on state:

```python
for page in reader.pages:
    for ref in page.get("/Annots", []):
        widget = ref.get_object()
        if widget.get("/FT") == "/Btn":
            print(widget.get("/T"), list(widget["/AP"]["/N"].keys()))
```

If `/T` is absent on a widget, inspect its `/Parent` for the field name. Use the on-state key **including its leading slash** as that checkbox’s checked value; use `"/Off"` when unchecked. Leave the court-use field empty.

Use `Decimal`, not binary floating point, for USD. Filter `status == "unpaid"` **before** calculating both the total and date range. Parse ledger dates with `datetime.strptime(value, "%m/%d/%Y")`; parse a written-out filing date with `"%B %d, %Y"` (adjust only if the input’s actual spelling requires it). Format dates with `.strftime("%Y-%m-%d")`, money with `f"{total:.2f}"`, and a phone number by retaining its 10 digits and inserting hyphens. The threshold condition is strictly `total > Decimal("2500.00")`.

After constructing a dictionary keyed by the PDF’s exact field names:

```python
writer = PdfWriter()
writer.append(reader)  # carry over pages and form structure
writer.update_page_form_field_values(
    writer.pages[0], field_values, auto_regenerate=False
)
with (root / "claim_form_filled.pdf").open("wb") as f:
    writer.write(f)
```

Reopen the output with `PdfReader`; inspect `get_fields()` for text values (including an empty `case_number`) and each checkbox widget’s `/V` and `/AS` states.
