# Sorry dependency audit of a Lean 4 project

The directory `/root/work/project/` contains several Lean 4 source files (`*.lean`, non-recursive). Before the proofs can be accepted, every declaration that relies on `sorry`, directly or indirectly, must be identified. You do not need a Lean toolchain. This is a static analysis of the source text.

Use these conventions:

- **Declaration.** A declaration starts on a line that begins at column 0 with `theorem `, `lemma ` or `def `, followed by its name. A declaration's text runs from that line up to, but not including, the next declaration line in the same file, or to the end of the file. Lines before the first declaration of a file belong to no declaration. Names are unique across the project.
- **Comments.** Everything from `--` to the end of a line is a comment and must be ignored.
- **Identifiers.** An identifier is a maximal run of characters from `[A-Za-z0-9_']` that starts with a letter or underscore. A dot separates identifiers, so `foo.trans` contains `foo`.
- **Direct use.** A declaration uses `sorry` directly if its non-comment text contains the identifier `sorry`.
- **References.** A declaration references another declaration if its non-comment text contains that declaration's name as an identifier. Self-references are ignored. File order does not matter.
- **Tainted.** A declaration is tainted if it uses `sorry` directly, or if it references a tainted declaration. Apply this transitively.

Write `/root/work/sorry_report.json` containing a JSON object with these fields:

- `declarations`: the total number of declarations (integer).
- `direct`: the names of the declarations that use `sorry` directly.
- `tainted`: the names of all tainted declarations, including the direct ones.
- `clean_theorems`: the names of `theorem`/`lemma` declarations that are not tainted.

Each list must be sorted in ascending order using plain string comparison.
