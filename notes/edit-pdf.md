**Tools.** Use Python with PyMuPDF (`import fitz`). It is pre-installed and keeps the text layer extractable. Do not use pdf-lib/JS, rasterizing, `get_pixmap`, image round-trips, or strikethrough lines.

**Inspect cheaply first.**
- `cat /root/input/input.txt` (it is usually short). It is the source of truth: it holds new values plus instructions such as fill blanks, sign, date, or redact/mask an ID.
- `python3 -c "import fitz;d=fitz.open('/root/input/input.pdf');print(len(d));[print(i,p.rect,repr(p.get_text()[:1500])) for i,p in enumerate(d)]"`. Raise or lower the slice to suit the budget.
- Check for real form widgets: `python3 -c "import fitz;d=fitz.open('/root/input/input.pdf');print([(p.number,w.field_name,w.field_value,w.rect) for p in d for w in p.widgets()])"`.
  - If widgets exist, fill them with `w.field_value = "..."; w.update()`. This is the right place for answers.
- For each label you must fill, get its exact position, including words to its right and lines below:
  - `page.get_text("words")` gives tuples `(x0,y0,x1,y1,word,...)`.
  - `page.search_for("Label")` gives rects.
  - `page.get_drawings()` shows underlines and box lines. Find the y of the line next to a blank field so the text sits on the line, inside the box.

**Parsing input.txt.** Use key:value lines. Strip a leading `- ` and split on the first `:`. Read any free-text instructions too (e.g. "mask student ID showing last 4 digits", "use today's date", "sign with full name").

**Decide per field by comparing the PDF with the txt.**
- **Already correct:** leave it alone. Never add a duplicate.
- **Wrong or outdated: replace in place.**
  1. `r = page.search_for(old)[0]`.
  2. `page.draw_rect(r, color=(1,1,1), fill=(1,1,1), width=0)`.
  3. `page.insert_text((r.x0, r.y1 - 2), new, fontsize=fs, color=(0,0,0))`.
  - Use the same x as the old text, never `r.x1 + offset`.
  - Keep the white rect tight to the value only, so labels stay visible. If the old value shares a line with its label, search for the value string itself, not the label.
  - If several matches exist, pick the one near the right label (compare y with the label's rect).
- **Empty blank or field.** Insert to the right of the label: `(label.x1 + 5, label.y1 - 1)`. If there is an underline or box, use the line's y minus 2 as the baseline and start x just after the label or the line start. Make sure the text stays within the box width; shrink fontsize if needed.
- **Date.** Use `datetime.now().strftime(...)`, in the format implied by the doc or instructions (default `%Y/%m/%d`).
- **Signature.** Insert the person's full name at the signature line.
- **Sensitive data: TRUE redaction, not draw_rect.** A white rect leaves the text extractable.
  ```python
  r = page.search_for(orig)[0]
  page.add_redact_annot(fitz.Rect(r.x0, r.y0+1, r.x1, r.y1-1), fill=(1,1,1))   # WHITE, never black
  page.apply_redactions()
  page.insert_text((r.x0, r.y1-2), "****"+digits[-4:], fontsize=fs)
  ```
  - The masking convention is `"****" + last 4 digits` unless the txt says otherwise.
  - Keep the redact rect tight so neighbouring labels are not removed.
  - Call `apply_redactions` before inserting other text in that area, or apply redactions first in the script.

**Font size.** Match the original by checking `page.get_text("dict")` spans for `size`, or use 10–11pt. Use the default font `helv`. If text contains non-Latin-1 characters, pass `fontname` with a fontfile.

**Script plan.**
1. Write `/root/edit.py`: open the input, apply redactions, do replacements, fill blanks, then `doc.save("/root/output/output.pdf", garbage=3, deflate=True)`.
2. Run `mkdir -p /root/output` before saving.
3. Keep all text and labels intact apart from the edited values.

**Verify, printing only short output.**
- `python3 -c "import fitz;print(fitz.open('/root/output/output.pdf')[0].get_text()[:1500])"`. Confirm:
  - New values are present.
  - Redacted originals are absent.
  - Labels still exist.
  - No duplicate old+new pairs (the old value may still be extractable only for draw_rect replacements; that is expected).
- Optionally check with pypdf: `from pypdf import PdfReader; PdfReader(path).pages[0].extract_text()`.
- Confirm each inserted string's position with `search_for(new)`: it should be near its label, on or above the line, and inside the box.

**Output.** One PDF at `/root/output/output.pdf`, same pages as the input, with the text layer preserved (not flattened).
