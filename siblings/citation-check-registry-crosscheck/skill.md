## Reference notes

Use Python’s standard-library `csv`, `json`, and `re`; the trusted CSV is the only metadata source needed. The citation skill’s search and online DOI-validation tools are unnecessary here.

- Read registry rows with `csv.DictReader(f)`; columns are `doi,title,year,first_author`. Index by normalized DOI. Do **not** compare `first_author`: it is not one of the requested checks.
- BibTeX entries begin with `@type{citation_key,`. Field names are case-insensitive; each field is on its own line. Parse the key from the entry header, then field lines by splitting at the **first** `=`. Remove a trailing field-separating comma before unwrapping a value. Unwrap one enclosing `{...}` or `"..."` pair (bare years have neither). Nested braces inside titles are content, not entry boundaries; avoid splitting the entire file on `}`.
- DOI normalization: `strip().lower()`, then remove **one** matching leading prefix from `https://doi.org/`, `http://doi.org/`, `https://dx.doi.org/`, `http://dx.doi.org/`, `doi:`. Apply it to registry DOIs too.
- Title normalization: delete every `{`, `}`, and `\`; lowercase; replace each non-alphanumeric character with a space; collapse whitespace and trim. `str.isalnum()` avoids treating underscores as alphanumeric:

```python
def norm_title(s):
    s = s.replace("{", "").replace("}", "").replace("\\", "").lower()
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())
```

Classify in strict order: absent/empty DOI → `missing_doi`; normalized DOI absent from registry → `unknown_doi`; normalized titles unequal → `title_mismatch`; years unequal → `year_mismatch`; otherwise genuine. Compare the unwrapped, trimmed entry year with the CSV year as strings. Record only non-genuine keys; write JSON with `fake_keys` sorted ascending and `reasons` containing exactly those keys.

Cheap workflow: inspect a small sample of both files, write one local parser-and-audit script, run it, then inspect the resulting JSON and its key count.
