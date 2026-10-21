**Tools.** Use python-docx (`from docx import Document`). If the import fails, run `pip install python-docx`. Read the data with `json.load`. For final verification, open the saved .docx as a zip and grep the XML for leftover `{{`.

**Inspect cheaply first. Never print whole files.**
- `ls /root; python3 -c "import json;d=json.load(open('/root/employee_data.json'));print(type(d), list(d)[:50] if isinstance(d,dict) else len(d))"`
  - Check whether keys are flat UPPER_CASE names that match the placeholders, or nested dicts and lists.
  - Check whether there are several employees.
  - Check the exact value and spelling of `RELOCATION_PACKAGE` (Yes/No, true/false).
  - Find the JSON file wherever it is (`find / -name employee_data.json 2>/dev/null`).
- List every placeholder in the template:
  - `python3 -c "import zipfile,re;z=zipfile.ZipFile('offer_letter_template.docx');[print(n,sorted(set(re.findall(r'\{\{[A-Z_]+\}\}',re.sub(r'<[^>]+>','',z.read(n).decode()))))) for n in z.namelist() if n.endswith('.xml')]"`
  - This strips XML tags, so placeholders split across runs still show up.
  - It also shows which parts contain them: document.xml, header*.xml, footer*.xml.
- Compare the placeholder names with the JSON keys.
  - If the JSON is nested, flatten it: use the leaf keys, upper-cased.
  - If a placeholder has no exact match, map it by hand.
  - Print only the key list and any unmatched names.

**Core pitfall: split placeholders.** Word splits `{{CANDIDATE_FULL_NAME}}` across several runs, so a run-level `.replace` misses it. Work at paragraph level:
1. Read `text = para.text`.
2. Substitute all `\{\{([A-Z_]+)\}\}` matches whose key is in the data, using `str(value)`.
3. If the text changed, set `runs[0].text = new_text` and set every other run's `.text = ''`. This keeps the first run's formatting.

**Visit every container. Pitfalls are forgetting headers/footers and nested tables.**
- `doc.paragraphs`.
- `doc.tables`, recursing: `for row in t.rows: for cell in row.cells: paras(cell.paragraphs); for nt in cell.tables: recurse(nt)`.
- Each `section` in `doc.sections`. For each of `header`, `footer`, `first_page_header`, `first_page_footer`, `even_page_header` and `even_page_footer`, process both its `.paragraphs` and its `.tables`.

**Conditional section `{{IF_RELOCATION}}...{{END_IF_RELOCATION}}`.**
- The markers may sit inside one paragraph or in separate paragraphs, with body paragraphs between them. Handle both cases.
- **Single-paragraph case** (both markers in the same paragraph):
  - If relocation is Yes, delete just the two marker strings and keep the inner text.
  - If No, delete the marker-to-marker span.
- **Multi-paragraph case** (walk the body element list in order):
  - Find the paragraph containing the IF marker and the paragraph containing the END marker.
  - If Yes:
    - Remove the marker text.
    - If a marker paragraph becomes empty, remove the element: `p._element.getparent().remove(p._element)`.
    - Keep and fill the paragraphs in between.
  - If No, remove every paragraph from the IF paragraph to the END paragraph, inclusive.
- Decide include with `str(data.get('RELOCATION_PACKAGE','')).strip().lower() in ('yes','true','y','1')`.
- Process conditionals before or together with the normal replacement. Make sure no `IF_`/`END_IF_` text survives.
- Placeholders inside the kept section (for example a relocation amount) must also be filled.

**Script plan.** Write a single file, `/root/fill.py`:
1. Load the JSON and build a flat `data` dict (UPPER_CASE keys to strings). Keep the values' original formatting; don't re-format numbers or dates unless the JSON lacks the formatted form.
2. `doc = Document(template_path)`.
3. Handle the conditional block or blocks.
4. Replace placeholders in every paragraph of the body, tables (recursive), headers and footers.
5. `doc.save('/root/offer_letter_filled.docx')`.

Snippet core:
```python
import re,json
from docx import Document
PAT=re.compile(r'\{\{([A-Z_]+)\}\}')
def fix(p):
    t=p.text; n=PAT.sub(lambda m: str(data[m.group(1)]) if m.group(1) in data else m.group(0), t)
    if n!=t and p.runs:
        p.runs[0].text=n
        for r in p.runs[1:]: r.text=''
def table(t):
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs: fix(p)
            for nt in c.tables: table(nt)
```
For conditionals in the body, scan `list(doc.paragraphs)` for indexes `i_start` and `i_end` whose `.text` contains the markers, then keep or delete as described above. Do the same inside table cells if the markers appear there.

**Verify** after running:
- Re-run the zip/regex inspection on `/root/offer_letter_filled.docx` and confirm that no `{{` and no `IF_RELOCATION` remain in any XML part.
- `python3 -c "from docx import Document;d=Document('/root/offer_letter_filled.docx');print(sum(len(p.text) for p in d.paragraphs))"` confirms the file opens.
- Spot-check a few lines, such as the candidate name and position lines, with grep on `p.text` instead of printing everything.
- Check that the relocation text is present if the value is Yes and absent if No.
- If any placeholder is left unfilled, find its matching JSON key and map it.

**Output requirements:**
- Exactly `/root/offer_letter_filled.docx`, a valid .docx built from the template.
- All `{{...}}` placeholders replaced with the JSON values.
- The relocation section kept only if `RELOCATION_PACKAGE` is Yes.
- All IF/END_IF markers removed.
- Formatting preserved wherever possible.
