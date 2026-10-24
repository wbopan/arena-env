## Reference notes

Use **pypdf** to update the AcroForm fields themselves. Drawing text over the page would leave stale field values behind; flattening or rasterizing would remove the interactive fields.

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("/root/work/onboarding_form.pdf")
print(len(reader.pages))
print(list((reader.get_fields() or {}).keys()))  # inspect field names cheaply

writer = PdfWriter()
writer.append(reader)  # retain the page and form structure
writer.update_page_form_field_values(
    writer.pages[0],
    field_values,         # dict: exact PDF field name -> string value
    auto_regenerate=False,
)
writer.write("/root/work/onboarding_filled.pdf")
```

Parse only bullet lines, splitting at the **first** colon so colons in values survive:

```python
notes = {}
for line in open("/root/work/update.txt", encoding="utf-8"):
    line = line.strip()
    if line.startswith("- ") and ":" in line:
        key, value = line[2:].split(":", 1)
        notes[key.strip()] = value.strip()
```

Select the legal name, employee number, **current** team, first day, and yearly **base** pay from the note’s keys; ignore nickname, preferred name, previous team, and unrelated pay. Keep name and employee number exactly as written. Parse the first day according to its actual input format, then format with `date.strftime("%m/%d/%Y")`.

Use decimal arithmetic for pay, not binary floats:

```python
from decimal import Decimal, ROUND_HALF_UP

cent = Decimal("0.01")
annual = Decimal(cleaned_yearly_base_pay)
annual_text = f"{annual.quantize(cent, rounding=ROUND_HALF_UP):.2f}"
monthly_text = f"{(annual / Decimal(12)).quantize(cent, rounding=ROUND_HALF_UP):.2f}"
```

`cleaned_yearly_base_pay` should contain only the numeric amount (remove any currency symbol and thousands separators). Assign **all six** field names in `field_values`, even when an existing value appears correct. After writing, reopen the output with `PdfReader`: confirm one page, the same six fields, and each field’s stored `/V` value.
