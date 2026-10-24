## Reference notes

Use `pypdf`, `python-docx`, and `python-pptx` to read the files without changing them. The DOCX skill’s editing and conversion workflows are unnecessary here.

```python
from pypdf import PdfReader
from docx import Document
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
```

- **PDF:** `reader = PdfReader(path)`; units = `len(reader.pages)`. Read every page with `page.extract_text() or ""`. Extraction reads embedded text, not text visible only in an image.
- **DOCX:** `doc = Document(path)`; use `doc.paragraphs` for *body paragraphs*, not tables, headers, or footers. Units = `sum(bool(p.text.strip()) for p in doc.paragraphs)`. Classify using the text of **all** body paragraphs, including empty ones harmlessly.
- **PPTX:** `prs = Presentation(path)`; units = `len(prs.slides)`. Visit shapes on every slide. For a text frame, use `shape.has_text_frame` and `shape.text_frame.text`; for a table, use `shape.has_table` and each `cell.text` in `shape.table.rows`/`row.cells`. Recurse into grouped shapes when `shape.shape_type == MSO_SHAPE_TYPE.GROUP`, using `shape.shapes`.

**Matching:** The specified “word” contains only ASCII letters. `re.findall(r"[a-z]+", text.lower())` produces whole words under that definition; count exact keyword tokens, not substrings. Join extracted pages/paragraphs/shapes with a separator such as `"\n"` so unrelated text fragments cannot form a new word. Sum occurrences across each subject’s five keywords. Resolve equal totals by sorting subject names alphabetically, then selecting the first among those with the maximum total.

**Output workflow:** Cheaply list the inbox filenames; write one Python script to read each file according to its suffix, count and classify, and write CSV with `csv.writer` and `open("/root/work/manifest.csv", "w", newline="", encoding="utf-8")`. Write `["file", "subject", "units"]` first and rows in ascending bare-filename order. Run the script, then inspect the CSV’s header, row count, filenames, and integer units. Leave inbox files untouched.
