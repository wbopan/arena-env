# Cross-check a bibliography against a local DOI registry

A co-author's bibliography `/root/work/refs.bib` may contain fabricated or corrupted references. You also have an offline, trusted metadata dump `/root/work/registry.csv` with columns `doi,title,year,first_author`. It has one row per genuine publication.

Classify every BibTeX entry. Apply these checks in order and assign the first reason that applies:

1. `missing_doi`: the entry has no `doi` field, or the field is empty.
2. `unknown_doi`: the normalized DOI does not appear in the registry.
3. `title_mismatch`: the normalized entry title differs from the normalized registry title for that DOI.
4. `year_mismatch`: the entry's year differs from the registry year for that DOI.

Entries that pass all four checks are genuine.

Normalization rules:
- **DOI**: trim and lowercase. Then remove one leading prefix if present: `https://doi.org/`, `http://doi.org/`, `https://dx.doi.org/`, `http://dx.doi.org/` or `doi:`.
- **Title**: remove all braces `{` `}` and backslashes, then lowercase. Replace every run of non-alphanumeric characters with a single space, then trim. Normalize registry titles the same way.

Field names are case-insensitive. Values may be wrapped in braces or quotes, or may be bare numbers. Each field is on its own line.

Write `/root/work/audit.json` in this form:

```json
{"fake_keys": ["key1", "key2"], "reasons": {"key1": "unknown_doi", "key2": "missing_doi"}}
```

`fake_keys` lists the citation keys of all non-genuine entries, sorted ascending. `reasons` maps each of those keys, and only those keys, to its reason string.
