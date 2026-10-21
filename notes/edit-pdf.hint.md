1. `cat /root/input/input.txt`; print each page's `get_text()` (sliced), its widgets, and the words/drawings near the target labels using PyMuPDF.
2. Write one fitz script that:
   - redacts sensitive values with `add_redact_annot(fill=(1,1,1))` + `apply_redactions()`, then inserts the mask;
   - replaces wrong values with a tight white `draw_rect` + `insert_text` at the same x0;
   - fills blanks on their lines or in their widgets;
   - skips values that are already correct.
3. Save to `/root/output/output.pdf`, re-extract the text, and check that new values are present, redacted originals are gone, there are no duplicates, and labels are intact.
