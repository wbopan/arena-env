## Reference notes

Use Python’s standard library to read the **listed atom-site data directly**. Do not use `Structure.from_file()` or symmetry analysis: structure parsers may expand, reorder, or reinterpret sites, whereas this task depends on the original row order and listed fields.

- Inspect the three CIFs briefly to identify their atom-site loop headers. A CIF `loop_` has consecutive `_...` column names followed by data tokens; find the loop containing the Wyckoff letter, multiplicity, and `_atom_site_fract_x`, `_atom_site_fract_y`, `_atom_site_fract_z` columns. Select columns **by header name, not position**. Rows need not be sorted.
- Preserve file order. On encountering a letter for the first time, retain that row’s listed multiplicity and x/y/z tokens; ignore later rows with the same letter. Do not use occupancy.
- CIF values can be quoted, and `#` introduces comments outside quotes. `shlex` can tokenize simple whitespace/quoted atom-site rows (`shlex.split(line, comments=True)`), but it does **not** implement CIF semicolon-delimited multiline text fields. Inspect the small files before choosing a tokenizer; keep loop row boundaries correct if tokens wrap across lines.
- Decimal coordinates may carry CIF uncertainty notation such as `0.3333(2)`; remove the trailing parenthesized uncertainty before numeric conversion if present.

For each retained coordinate, reduce modulo 1 **before** rational approximation. `Fraction.limit_denominator(12)` finds the nearest fraction subject to that denominator bound; `str(Fraction)` already produces reduced strings, including `0` and integers without `/1`:

```python
from fractions import Fraction
import re

def rational_coordinate(token):
    token = re.sub(r"\(\d+\)$", "", token)
    return str((Fraction(token) % 1).limit_denominator(12))
```

A small script can iterate `Path("/root/work/cifs").glob("*.cif")`, use `path.name` for each top-level key, and write the resulting mapping with `json.dump(..., ensure_ascii=False)` to a file opened with `encoding="utf-8"`. After running it, read the JSON back and compare each file’s letter set and retained rows against the CIF atom-site loops.
