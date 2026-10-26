## Reference notes

Use Python’s standard library (`pathlib`, `shlex`, `re`, `math`, `json`); no crystallographic structure parser is needed. A structure loader may expand symmetry or change the listed sites, which this task forbids.

- Inspect both CIFs briefly to locate `_cell_length_a`, `_cell_length_b`, `_cell_length_c` and the `loop_` containing `_atom_site_label` and `_atom_site_fract_x`, `_atom_site_fract_y`, `_atom_site_fract_z`. Select loop columns **by header name**, not fixed position. Keep one record per listed row; use its label verbatim.
- CIF values may be quoted, and cell lengths or coordinates may include parenthesized standard uncertainties, e.g. `5.432(1)`. Strip the trailing parenthesized uncertainty before `float()`. Check the actual files before choosing a lightweight tokenizer: `str.split()` does not respect quotes; `shlex` can handle simple quoted rows but is not a full CIF parser (notably semicolon-delimited multiline fields).
- For two *different row indices* with fractional coordinates `p`, `q` and lengths `(a, b, c)` in Å:
  ```python
  delta = [x - y for x, y in zip(p, q)]
  wrapped = [t - round(t) for t in delta]
  distance = math.sqrt(sum((t * length)**2
                           for t, length in zip(wrapped, (a, b, c))))
  ```
  At a half-cell difference, either nearest-integer choice gives the same distance. Never include a row’s own periodic images. Do not expand Wyckoff multiplicities or symmetry operations.
- Compare **unrounded** distances. Replace the current choice if the new distance is smaller by more than `1e-9` Å; if distances differ by at most `1e-9` Å, choose the lexicographically smaller **label**. Round only the selected distance with `round(distance, 4)` for the JSON number.
- Process each CIF independently. Write one UTF-8 JSON object keyed by each file’s basename (including `.cif`), then by every listed label; each value contains only `neighbor` and `distance_angstrom`. After writing, read the JSON back and check that its file keys, site-label keys, and value fields match the input rows.
