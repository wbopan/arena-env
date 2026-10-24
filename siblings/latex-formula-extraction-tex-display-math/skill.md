## Reference notes

The input is **LaTeX source**, not a PDF. Use Python’s standard-library `pathlib` and `re`; PDF conversion tools would change the source tokens and spacing.

- Read as text, then discard lines whose first non-whitespace character is `%`:
  ```python
  from pathlib import Path
  import re

  text = Path("/root/work/paper.tex").read_text(encoding="utf-8")
  text = "\n".join(line for line in text.splitlines()
                   if not line.lstrip().startswith("%"))
  ```
  Do not discard lines merely because they contain `%`: the specified rule concerns *whole lines*.
- Scan the remaining text **left to right**, pairing each opener with its corresponding closer: `\begin{equation}` / `\end{equation}`, the starred equivalents, `\[` / `\]`, and `$$` / `$$`. Capture only the intervening body. Bodies can span lines or share a line with other text or displays. Ignore `$...$`. In regex patterns, use raw strings and escape literal backslashes and dollar signs; `re.DOTALL` lets `.` cross newlines. An ordered scanner also preserves document order across the four forms.
- Normalise **each captured body**, in order: remove `\label{...}` commands; collapse whitespace with `re.sub(r"\s+", " ", body).strip()`; remove **one** final `,` or `.` if present, then strip again. Do not strip other punctuation or rewrite LaTeX commands.
- Write one `$$`-wrapped body per line, with no empty lines. A final newline is fine. Inspect a small portion of the source and the resulting output, particularly multiline displays, starred environments, and commented-out displays.
