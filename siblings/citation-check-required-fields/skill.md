## Reference notes

- Use Python’s standard-library `re` and `csv`; no citation lookup or BibTeX formatting is needed. The supplied citation notes identify `journal` for articles, `booktitle` for proceedings, and `publisher` for books. **Follow this task’s required-field table exactly:** a book needs `author` even if it has `editor`; an article’s `booktitle` cannot replace `journal`.
- BibTeX entries begin with `@type{CitationKey,` (occasionally `@type(CitationKey,`). Preserve the citation key’s spelling; lowercase the type and field names. Since every field is on its own line, parse entry headers and field lines separately. Split field lines at the **first** `=` only; a value may contain `=` or commas. Remove an optional trailing field comma before cleaning the value. Do not mistake an entry’s closing `}` for a field.
- Apply the specified cleaning literally: remove surrounding double quotes, remove **all** `{` and `}` characters, then trim leading/trailing whitespace. An absent field or an empty cleaned value is missing. For `year`, also require `re.fullmatch(r"[0-9]{4}", cleaned)`; `[0-9]` specifies four ASCII digits. Check only fields required by that entry’s type, in the table’s order.

```python
required = {
    "article": ("author", "title", "journal", "year"),
    "inproceedings": ("author", "title", "booktitle", "year"),
    "book": ("author", "title", "publisher", "year"),
    "misc": ("author", "title", "year"),
}
```

Workflow: cheaply inspect a few lines of `/root/work/library.bib` to confirm its header and field layout; write one line-oriented parser and validation script; write `/root/work/missing_fields.csv` using `csv.writer` with header `key,entry_type,missing_fields`. Join missing names with `";"`, retain only entries with missing fields, and sort rows with `key=lambda row: row[0]` (plain, case-sensitive string order). Run the script, then inspect the CSV header and a few rows.
