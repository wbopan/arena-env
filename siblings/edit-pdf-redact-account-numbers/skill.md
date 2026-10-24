## Reference notes

Use **PyMuPDF** (`import fitz`) for true PDF redaction. A white rectangle drawn over an account number only hides it visually; the original remains extractable. Do not rasterize the pages.

```python
import re
import fitz

doc = fitz.open("/root/work/register.pdf")
for page in doc:
    print(page.get_text())                 # inspect lines and column structure
    words = page.get_text("words")         # tuples: x0,y0,x1,y1,text,...
    spans = [
        span
        for block in page.get_text("dict")["blocks"]
        if "lines" in block
        for line in block["lines"]
        for span in line["spans"]
    ]
```

- Identify account values **in customer rows and the account column**, not merely by searching for digits everywhere. For an isolated token, `re.fullmatch(r"\d{10}", word)` distinguishes a 10-digit account from the 8-digit batch footer. Mask with `"******" + account[-4:]`.
- Capture each value’s bounding box and replacement position **before** changing the page. `page.search_for(account)` returns matching rectangles; check matches if an account occurs more than once. Use a box that encloses every account glyph but does not intersect neighboring column text. Fixed offsets such as `y0 + 8` are not reliably safe.
- For true removal, add all targeted redactions on a page, then apply them:
  ```python
  page.add_redact_annot(fitz.Rect(x0, y0, x1, y1), fill=(1, 1, 1))
  # after all annotations on this page:
  page.apply_redactions()
  ```
  Reinsert masked text at the **original x position and baseline** using `page.insert_text((x, baseline_y), masked, fontsize=..., color=(0, 0, 0))`. A span’s `origin` supplies its baseline and `size` its font size when the account starts that span. A word rectangle’s `y1` is not necessarily the baseline.

**Extraction-order pitfall:** text inserted after redaction may be appended to the PDF’s text stream, so an extractor can report masked accounts *after* the footer instead of inside their rows, even when they look correctly positioned. Check extracted lines from the saved PDF without relying solely on visual placement or coordinate-sorted extraction. If insertion cannot preserve line order, rebuild the affected page’s text layer in original line/span order, replacing only account strings, rather than appending isolated replacements.

Save to `/root/work/register_redacted.pdf` with a non-incremental save (for example, `doc.save(path, garbage=4, deflate=True)`). Reopen it and compare extracted text **page by page** against the original with only the account substitutions; also confirm that no original 10-digit account string remains extractable.
