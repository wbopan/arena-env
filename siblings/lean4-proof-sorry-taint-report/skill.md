## Reference notes

Use **Python standard library** (`pathlib`, `re`, `json`); this is a source-text audit, so Lean, `lake`, LSP, and proof-analysis commands are unnecessary. The supplied Lean skills discuss proof development, not an API for this static analysis.

- Read only non-recursive `*.lean` files: `Path("/root/work/project").glob("*.lean")`. Process each file independently; declaration boundaries never cross files.
- Strip line comments before analysis: `line.split("--", 1)[0]`. Under the task’s convention, there is no need to parse other Lean comment syntax.
- Detect declaration starts **only at column 0**, with `theorem `, `lemma `, or `def `. Text before the first start belongs to no declaration. Retain each declaration’s kind, name, and non-comment text through the line before the next start (or EOF).
- Tokenize with maximal runs of `[A-Za-z0-9_']+`, then keep runs whose **first character** is a letter or underscore. This avoids falsely treating the `foo` portion of `1foo` as an identifier. A dot is a separator: `foo.trans` yields `foo` and `trans`. Match names and `sorry` against whole tokens, not substrings.
- Build references after collecting **all** names, so later declarations and other files can be referenced. Exclude a declaration’s own name from its references. Direct declarations are those with a `sorry` token.
- Compute the least transitive tainted set: start with direct declarations; repeatedly add any declaration referencing one already tainted until nothing changes. Cycles are handled by this fixed point.
- `clean_theorems` includes only untainted `theorem` and `lemma` names, not `def` names. Sort each output list with Python’s `sorted()` and write the JSON object using `json.dump(...)`.

Compact workflow: briefly inspect filenames or a few lines to confirm layout; write one Python script to parse, collect references, propagate taint, and emit `/root/work/sorry_report.json`; run it, then inspect the JSON and its counts.
