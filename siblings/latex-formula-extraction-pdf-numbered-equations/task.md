You are building an equation index for a technical note delivered as a PDF.

Input: `/root/work/tech_note.pdf`, three pages of plain text. Each displayed formula is printed as raw LaTeX source text on its own line.

Some formula lines are **numbered**. The line ends with an equation tag `(n)`, where `n` is a positive integer in parentheses. The tag is the last thing on the line and is separated from the formula by whitespace.

Other formula lines carry no tag. Ignore them. Body sentences may cite equations, for example "as shown in (3).". These citations are not tags, and those sentences must be ignored.

For every numbered equation, record:

- `number`: the integer from the tag.
- `page`: the 1-based page number where it appears.
- `latex`: the formula text with the tag removed.
  - Replace runs of whitespace with a single space and trim both ends.
  - Remove a trailing comma or period, which is sentence punctuation, and trim again.
  - Make no other changes. Keep the LaTeX exactly as printed.

Output: write `/root/work/equations.json` as a JSON array of objects, sorted by `number` in ascending order. Each object has exactly the keys `number` (integer), `page` (integer) and `latex` (string). Example element:

```json
{"number": 4, "page": 1, "latex": "\\mathbf{v} = \\left( a_1 + a_2 \\right)^{3}"}
```

Include every numbered equation in the document and nothing else.
