## Reference notes

Use `pypdf` to extract text **page by page**, retaining the page number:

```python
from pypdf import PdfReader

reader = PdfReader("/root/work/tech_note.pdf")
for page_number, page in enumerate(reader.pages, start=1):
    for line in (page.extract_text() or "").splitlines():
        # inspect or classify this printed line
        ...
```

A candidate tag is a **positive integer at the end of a line**, preceded by whitespace. Match within each line, not across line breaks:

```python
import re

tag = re.search(r"[ \t]+\(([1-9][0-9]*)\)[ \t]*$", line)
if tag:
    number = int(tag.group(1))
    formula = line[:tag.start()]
```

The tag pattern alone is insufficient: a body sentence can also end in `(3)`. Inspect the extracted lines and retain only standalone formula lines; ignore unnumbered formulas and prose citations. Check that extraction has preserved LaTeX backslashes and line boundaries. If needed, compare with the documented CLI alternative `pdftotext -layout input.pdf output.txt`, keeping page boundaries identifiable.

For an accepted formula, collapse whitespace with `" ".join(formula.split())`. Then remove **one** trailing comma or period, if present, and trim again; do not otherwise edit the LaTeX. Sort records by integer `number`. Write a JSON array using standard-library `json.dump`; Python strings’ LaTeX backslashes will be escaped correctly in JSON.
