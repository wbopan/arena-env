1. Inspect the `employee_data.json` keys/structure and `RELOCATION_PACKAGE` with a python one-liner. List the template's placeholders per XML part using zipfile plus tag-stripping regex, since placeholders are split across runs.
2. Write `/root/fill.py` using python-docx. Replace at paragraph level: substitute in `para.text`, put the result in the first run and blank the other runs. Cover the body, nested tables and all header/footer variants.
3. Handle `{{IF_RELOCATION}}..{{END_IF_RELOCATION}}`, which may span paragraphs: keep the content and drop the markers if Yes, delete the block if No.
4. Save to `/root/offer_letter_filled.docx`, then verify with zipfile/regex that no `{{` or IF markers remain and that key values appear.
