You are cleaning up the source of a short research note so its displayed equations can be reused elsewhere.

Input: `/root/work/paper.tex`, a LaTeX source file.

Extract every **display-math formula** in document order. A display formula is the body of any of these constructs:

- `\begin{equation} ... \end{equation}`
- `\begin{equation*} ... \end{equation*}`
- `\[ ... \]`
- `$$ ... $$`

A body may span several source lines. Inline math (`$...$`) is not display math and must be ignored. Any line whose first non-whitespace character is `%` is a LaTeX comment. Treat the whole line as absent, including any display blocks written entirely on commented lines.

Normalise each extracted body as follows:

1. Delete every `\label{...}` command.
2. Replace every run of whitespace, including newlines, with a single space, then trim both ends.
3. Remove a trailing comma or period, which is sentence punctuation, and trim again.

Do not otherwise change the LaTeX. Keep its tokens and spacing between tokens exactly as they appear in the source after the normalisation above.

Output: write `/root/work/display_formulas.md` with one formula per line and no blank lines. Wrap each formula as `$$<formula>$$`, for example:

```
$$x_{k} = \frac{\alpha^{3}}{y + 2}$$
$$\mathbf{v} = \left( a_1 + a_2 \right)^{4}$$
```

The number of lines must equal the number of non-commented display formulas in the file.
