# Required-field validation of a BibTeX file

Before a manuscript is submitted, the bibliography `/root/work/library.bib` must be checked for incomplete entries. In the file, every field is written on its own line.

Each entry's type (case-insensitive) determines its required fields. The fields are listed below in canonical order:

| type | required fields |
|---|---|
| article | author, title, journal, year |
| inproceedings | author, title, booktitle, year |
| book | author, title, publisher, year |
| misc | author, title, year |

A required field counts as missing in either of these cases:
- It is absent.
- Its value is empty after removing surrounding double quotes, all `{` and `}` characters, and leading or trailing whitespace.

In addition, `year` counts as missing unless its cleaned value is exactly four digits. Field names are case-insensitive. A field that is not required for the entry's type never satisfies another requirement. For example, a `booktitle` on an article does not count as its `journal`.

Write `/root/work/missing_fields.csv` with the header `key,entry_type,missing_fields`. Include one row for each entry that has at least one missing required field:
- `key`: the citation key exactly as written.
- `entry_type`: the entry type in lowercase.
- `missing_fields`: the missing field names in canonical order, joined with `;` and no spaces.

Sort the rows by key in ascending plain string order. Omit entries that have no missing fields.
