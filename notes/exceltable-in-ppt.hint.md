1. Run `unzip -l` on /root/input.pptx to find `ppt/embeddings/*.xlsx`. Grep the slide XML for `<a:t>` to read the updated rate (FROM, TO, value).
2. Load the embedded xlsx from bytes with openpyxl (formulas mode) and locate cell row=FROM, col=TO. Update it only if it is a hardcoded value; if it is a formula, update the hardcoded cell it references instead. Never replace formulas.
3. Rewrite the ZIP with Python zipfile into /root/results.pptx, replacing only the embedding entry and copying every other entry unchanged. Optionally run recalc.py first to restore cached values.
4. Reload results.pptx, check the new value and that formulas are unchanged, and confirm the entry list matches the input.
