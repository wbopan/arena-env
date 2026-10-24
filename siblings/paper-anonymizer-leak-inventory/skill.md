## Reference notes

Use **pypdf** for text extraction; no PDF modification is needed.

```python
from pypdf import PdfReader

reader = PdfReader(path)
pages = [page.extract_text() or "" for page in reader.pages]
lines = "\n".join(pages).splitlines()
```

PDF text extraction can change spacing or wrap a bibliography entry across lines. Inspect a small sample of page 1 and the lines around `References` before settling on parsing expressions. Locate section boundaries with `line.strip() == "Abstract"` and `line.strip() == "References"`; do not include the References line or anything after it when finding emails or arXiv IDs.

- Page 1: line 2 contains the ordered author list. Split at `, ` **between names**, then remove each name’s trailing square-bracket markers (such as ` [1,2]`). Do not split the whole line on commas: markers can contain commas.
- Between the author line and `Abstract`, parse `[k] Institution Name`; sort institutions by integer `k`, not lexicographically.
- Search **all text before References**, not just page 1, for emails and `arXiv:YYMM.NNNNN`. A capture such as `r"arXiv:(\d{4}\.\d{5})(?:v\d+)?"` returns the bare ID and excludes an optional version. Lowercase emails; deduplicate and sort both lists.
- Self-citations are different: search bibliography entries after `References`. For each paper author `First Last`, form the pair `(Last, First[0])`. In each `[n]` entry, examine its **author-list portion**, not its title or venue, for an exact `Surname, F.` author (authors are separated by `;`). Compare both surname and initial; collect matching `n` as integers, unique and numerically sorted. If an entry wraps, join its continuation lines before parsing it.

Write the final object with standard-library `json.dump(data, file, indent=2)`, using the three PDF basenames as keys. After running the script, reopen the JSON and spot-check the field types and section boundaries against extracted text.
