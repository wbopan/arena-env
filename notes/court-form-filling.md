**Tools and form type.** SC-100 is a fillable AcroForm PDF (often with XFA as well). Use `pypdf`. Do not draw annotations by hand. The skill's workflow is: check for fillable fields, extract field info (id, page, type, checkbox checked value), map each field to the case facts, fill, then verify. If the helper scripts exist (`scripts/check_fillable_fields`, `extract_form_field_info.py`, `fill_fillable_fields.py`), you can use them. A direct pypdf script is just as good and uses fewer tokens.

**Step 1: inspect cheaply.** Never print the whole file. Dump one line per field showing page, short name, type, tooltip and checkbox states:
```python
from pypdf import PdfReader
r=PdfReader('/root/sc100-blank.pdf'); print(len(r.pages))
for pi,p in enumerate(r.pages):
  for a in p.get('/Annots') or []:
    a=a.get_object()
    if a.get('/Subtype')!='/Widget': continue
    f=a if '/T' in a else a['/Parent'].get_object()
    name=[];g=f
    while g is not None:
      if '/T' in g: name.insert(0,g['/T'])
      g=g.get('/Parent'); g=g.get_object() if g else None
    st=list(a['/AP']['/N'].keys()) if '/AP' in a and '/N' in a['/AP'] else ''
    print(pi+1,'.'.join(name)[-60:],f.get('/FT'),str(f.get('/TU',''))[:70],st)
```
Redirect the output to a file and use `grep` or `head` on it. Field names look like `SC-100[0].Page2[0].List1[0].Item1[0]...`. The `/TU` tooltips describe each field (e.g. "Plaintiff's name", "Phone", "Street address", "City", "State", "Zip", "Email"). Use `pdftotext -layout -f 2 -l 4 file - | head -80` only if a tooltip is unclear.

**What SC-100 asks, and the values to use** (pages 2–4; page 1 is notice and court-use material):
- **Court/case fields.** Case number, court name/address, hearing date/time/dept and clerk fields are court-filled. Leave them EMPTY.
- **Item 1, plaintiff.**
  - Name: Joyce He. Phone: 4125886066.
  - Street: 655 S Fair Oaks Ave. City: Sunnyvale. State: CA. Zip: 94086.
  - Email: he1998@gmail.com.
  - Mailing address is optional and differs from nothing given, so leave it empty.
  - Do not check "more than one plaintiff" or "fictitious business name". Leave the second-plaintiff fields empty.
- **Item 2, defendant.**
  - Name: Zhi Chen. Phone: 5125658878.
  - Street: 299 W Washington Ave. City: Sunnyvale. State: CA. Zip: 94086.
  - Agent-for-service, corporation and other-defendant fields stay empty.
- **Item 3, claim.**
  - Amount: 1500. Fill the number in the $ field; check what that field expects.
  - Why defendant owes: e.g. "Failed to return my security deposit after moving out, based on the signed roommate sublease contract."
  - When did this happen: there are date-started and through fields. Use 2025-09-30 and 2026-01-19. Leave the single-date field blank if a start/through pair exists.
  - How calculated: "The amount is listed on the signed roommate sublease contract."
- **Item 4, asked defendant to pay.** Check YES. If the form asks how, put "asked him multiple times via text, no response".
- **Item 5, venue.** Check the box for "where the defendant lives or does business", item (a)(1). Do not check any other reasons.
- **Item 6, zip code of the place in 5.** 94086.
- **Item 7, attorney-client fee dispute.** No.
- **Item 8, public entity.** No.
- **Item 9, more than 12 small claims in the past 12 months.** No; this is the first time.
- **Item 10, more than 2 claims over $2,500 this calendar year.** No.
- **Signature block.**
  - Date: 2026-01-19. Typed/printed name: Joyce He.
  - Leave the signature line blank unless a text signature field is clearly expected.
  - Second-plaintiff signature fields stay empty.
- **Repeated page headers.** The "Plaintiff (list names) / Case Number" header on pages 2–4: case number is court-filled, so leave it empty. Fill the header plaintiff name only if the tooltip marks it as plaintiff name; minimal filling is the instruction.
- **Dates.** All dates use the `YYYY-MM-DD` format.

**Checkbox pitfalls.**
- Yes/No pairs are often separate checkboxes, or radio kids under one parent.
- Set the value to the widget's own non-`/Off` state name from `/AP /N`; it may be `/1`, `/2`, `/On` or similar.
- For radio groups, set the parent `/V` to the chosen kid's state.
- On each widget, set `/AS` to its state if chosen, otherwise `/Off`.
- Identify the Yes box versus the No box by rect x-order or by tooltip.

**Step 2: fill script.** Write `/root/fill.py` with a dict mapping full field name to value:
```python
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,TextStringObject
w=PdfWriter(clone_from='/root/sc100-blank.pdf')
vals={...}  # text fields: str; checkboxes: '/1' style state name
for p in w.pages:
  w.update_page_form_field_values(p,{k:v for k,v in vals.items() if not v.startswith('/')},auto_regenerate=False)
# checkboxes manually: for each widget whose full name in vals and value starts with '/':
#   a[NameObject('/V')]=NameObject(v); a[NameObject('/AS')]=NameObject(v)  (set on parent too if kid)
w.set_need_appearances_writer(True)
if '/XFA' in w._root_object['/AcroForm']: del w._root_object['/AcroForm']['/XFA']
w.write('/root/sc100-filled.pdf')
```
Two notes on this script:
- `update_page_form_field_values` accepts qualified or partial names in recent pypdf. If a name does not match, set `/V` directly on the field object.
- Removing XFA makes viewers and checkers use the AcroForm values.

**Step 3: verify.** Run `python -c "from pypdf import PdfReader;print({k:v for k,v in PdfReader('/root/sc100-filled.pdf').get_fields().items() if v.get('/V') not in (None,'','/Off')})"`. Check all of the following:
- Every intended field is set, with the exact strings above.
- Checkboxes show the checked state.
- No court-use or optional fields are filled.
- Every date is in `YYYY-MM-DD` form.

**Output.** `/root/sc100-filled.pdf` must be the same form with its fields filled and the remaining fields empty.
