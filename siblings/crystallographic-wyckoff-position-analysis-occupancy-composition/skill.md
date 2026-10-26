## Reference notes

Use Python’s standard library to read the **atom-site loop directly**. Although pymatgen can read CIF structures (`Structure.from_file("structure.cif")` or `CifParser("structure.cif").get_structures()[0]`), structure expansion or composition reduction is unnecessary here and may obscure the supplied orbit multiplicities.

- Inspect the two files cheaply to identify the exact atom-site header names. CIF loops begin with `loop_`, followed by `_...` column names; **use header positions**, not assumed column order. Find the element-symbol, Wyckoff/site-symmetry multiplicity, and occupancy columns in the *same* atom-site loop. Do not substitute atom labels for element symbols.
- A data row is **one orbit**, contributing `Decimal(multiplicity) * Decimal(occupancy)` atoms of its element to that file’s conventional cell. Sum contributions from repeated elements; keep the files separate. Neither coordinates nor labels enter the calculation. Do not reduce or normalize the composition.
- CIF values are whitespace-separated, with quoted fields possible. `shlex.split(line, comments=True)` can tokenize simple data lines, but inspect for rows wrapped across lines or semicolon-delimited multiline fields before relying on a line-per-row parser. Stop a loop at the next CIF directive (such as `loop_`, a new `_tag`, or `data_`); do not absorb another loop’s data.
- Preserve decimal arithmetic throughout:
  ```python
  from collections import defaultdict
  from decimal import Decimal

  counts = defaultdict(Decimal)
  # For each parsed atom-site row, using indices found from its headers:
  counts[element] += Decimal(multiplicity_text) * Decimal(occupancy_text)
  # Output field: f"{counts[element]:.3f}"
  ```
- Short workflow: inspect filenames and relevant loop headers → write one script to parse each `*.cif` and accumulate counts → write UTF-8 TSV with tab-delimited header `file`, `element`, `effective_atoms`, sorting by `Path.name` then element symbol → run it and inspect the resulting file for three-decimal fields and no extra lines or columns.
