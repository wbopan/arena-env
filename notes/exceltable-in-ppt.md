**What the file looks like.** A .pptx is a ZIP archive. The embedded workbook is stored under `ppt/embeddings/`, usually as `Microsoft_Excel_Worksheet*.xlsx`. The slide holds a `p:graphicFrame` containing a `p:oleObj` with an `r:id`. That id resolves through `ppt/slides/_rels/slideN.xml.rels` to `../embeddings/....xlsx`. The table preview is a separate image in `ppt/media/` (emf or png). The text box is an ordinary `p:sp` whose text sits in `<a:t>` runs.

**Inspect cheaply (no full-file dumps):**
```bash
cd /root && unzip -l input.pptx | grep -Ei 'embed|slide[0-9]*.xml|media'
unzip -p input.pptx ppt/slides/slide1.xml | grep -o '<a:t>[^<]*</a:t>'
unzip -p input.pptx ppt/slides/_rels/slide1.xml.rels | grep -o 'Target="[^"]*"'
```
`python -m markitdown /root/input.pptx | head -50` also shows the text-box wording, for example "USD to EUR = 0.xx" or "1 GBP = x JPY".

If the embedding is an `oleObject*.bin` instead of an `.xlsx`, it is an OLE compound file and needs `olefile` to pull out the "Package" stream. Normally it is a plain `.xlsx`.

**Read the workbook with openpyxl, loading it twice:**
```python
import zipfile, io, openpyxl
z = zipfile.ZipFile('/root/input.pptx')
name = [n for n in z.namelist() if n.startswith('ppt/embeddings/')][0]
data = z.read(name)
wb = openpyxl.load_workbook(io.BytesIO(data))                 # formulas as strings
wbv = openpyxl.load_workbook(io.BytesIO(data), data_only=True) # cached values
ws = wb.active
for row in ws.iter_rows():
    print([(c.coordinate, c.value) for c in row if c.value is not None])
```
- Formula cells appear as strings starting with `=` (for example `=1/C2`, or `=B3*C4`).
- Row headers (from-currency) are usually in column A.
- Column headers (to-currency) are usually in row 1.
- The value at (row X, col Y) is the rate X→Y. The diagonal is 1.

**Find the cell to update.**
1. Parse the text box with a regex, for example `re.search(r'([A-Z]{3}).*?([A-Z]{3}).*?([\d.]+)', text)`.
2. Locate the row whose header equals the FROM currency and the column whose header equals the TO currency.
3. Pay attention to direction: row = from, column = to.
4. If the target cell holds a hardcoded number, overwrite it with `float(rate)`.
5. If the target cell is a formula (for example the inverse `=1/xx`), do NOT overwrite it. Instead update the hardcoded source cell it references (for example the reverse pair, set to `1/rate`), so the formula then yields the new rate.
6. Never convert any formula cell to a value.
7. Keep every other cell, the number formats and the sheet names unchanged.

**Save the workbook and re-pack the pptx.** Only the embedding entry changes. Copy every other ZIP entry byte-for-byte, with the same names, order and compression:
```python
ws[target] = new_value
buf = io.BytesIO(); wb.save(buf); new = buf.getvalue()
with zipfile.ZipFile('/root/input.pptx') as zin, \
     zipfile.ZipFile('/root/results.pptx', 'w', zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        zout.writestr(item, new if item.filename == name else zin.read(item.filename))
```
Do not touch the slide XML, the text box, the rels or `[Content_Types].xml`.

**Cached values (optional).** openpyxl drops the cached results of formulas, so a checker using `data_only=True` would see `None` for formula cells. To get cached values back:
1. Save the modified xlsx to `/tmp/emb.xlsx`.
2. Run the xlsx skill's recalc: `python recalc.py /tmp/emb.xlsx` (find it with `find / -name recalc.py 2>/dev/null`). It uses LibreOffice.
3. Re-check that the formulas are still strings starting with `=`.
4. Embed those bytes instead.

If recalc is not available, the plain openpyxl save is acceptable, because the formulas are preserved.

**Verify after writing:**
```python
z2 = zipfile.ZipFile('/root/results.pptx')
w2 = openpyxl.load_workbook(io.BytesIO(z2.read(name)))
# print the target cell and all formula cells;
# confirm the formula cells are identical to the original and the target equals the new rate
print(set(z.namelist()) == set(z2.namelist()))
```
Also confirm the file opens: `python -c "from pptx import Presentation; Presentation('/root/results.pptx')"`. Optionally compute the inverse/cross rates by hand to sanity-check that the formulas will evaluate to the new rate.

**Pitfalls:**
- Wrong direction (column→row instead of row→column).
- Rate parsed as a string instead of a float.
- Overwriting the formula cell itself.
- Re-zipping with the shell `zip` command in a way that reorders or alters entries (prefer Python zipfile).
- Editing the wrong slide's embedding when there are several (map them via the rels).
- Changing the preview image or the text box. Leave them as they are.

**Output:** `/root/results.pptx`. It must be identical to the input except for the updated cell value(s) inside the embedded Excel workbook, with all formulas intact.
