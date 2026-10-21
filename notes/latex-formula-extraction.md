**Goal:** produce `/root/latex_formula_extraction.md`. It should contain one `$$...$$` per line, one line for every display (own-line) formula in `latex_paper.pdf`, in page order. Then add a blank line. Then add one `$$...$$` line for each fixed version of a formula that has a syntax or typo error. Inline math (`$x$` inside sentences) is excluded.

**Primary tool: marker (PDF → Markdown with LaTeX).**
- Run `marker_single latex_paper.pdf --output_format markdown --disable_image_extraction --output_dir /root/marker_out`.
- Or, from the skill dir, run `python scripts/marker_to_markdown.py latex_paper.pdf --keep-temp`. The output goes to `latex_paper_marker/latex_paper/latex_paper.md`.
- In Python: `from scripts.marker_to_markdown import pdf_to_markdown; md = pdf_to_markdown("latex_paper.pdf", timeout=1200)`.
- Marker emits display math as `$$ ... $$` blocks. These may span several lines, so join the inner lines with spaces. Inline math appears as single `$...$` and must be ignored.
- Marker can be slow on the first run because it loads models. Use a long timeout and run it in the background if needed: `nohup ... > log 2>&1 &`, then poll `ls`.
- Do not print the whole md file. Grep instead: `grep -c '\$\$' file.md`.

**Cross-check tools (cheap):**
- `pdftotext -layout latex_paper.pdf - | sed -n '1,80p'` shows roughly where equations sit (indented lines, often ending with an equation number like `(3)`).
- `pdfinfo latex_paper.pdf` gives the page count.
- If a formula looks suspicious, render that page with `pdftoppm -png -r 100 -f N -l N latex_paper.pdf /tmp/p`. Only use this if you can view images.

**Extraction script (single Python file):**
```python
import re
md = open(path).read()
blocks = re.findall(r'\$\$(.*?)\$\$', md, flags=re.S)
out = []
for b in blocks:
    f = ' '.join(b.split())                      # one line
    f = re.sub(r'\\tag\{[^}]*\}', '', f)         # remove \tag{..}
    f = re.sub(r'\\qquad\s*\(\d+\)$|\(\d+\)\s*$', '', f.strip())  # eq numbers
    f = re.sub(r'(\\[,;!quad ]*)*[,.;]\s*$', '', f.strip())        # trailing , . ;
    f = re.sub(r'(\\quad|\\qquad|\\,|\\;|\\ )+$', '', f.strip()).strip()
    if f: out.append(f)
```
After the regexes, re-check the end of each formula. A trailing `.` or `,` can hide behind spacing like `\,` or `\quad`, or inside `\text{.}`; remove those too. Keep the formula body exactly as marker gave it. Do not prettify, reorder, or rename macros, because the extracted lines must render the same as the PDF.

**Filtering pitfalls:**
- Drop blocks that are not real display formulas. Examples: a stray single symbol, a table or figure misread as math, or a duplicate created by marker splitting one equation.
- If marker splits one PDF equation into two `$$` blocks, merge them. If it merges two separate display lines, split them. Compare against the pdftotext layout.
- Multi-line `aligned`/`align` environments stay as one line containing `\\`.
- Escape nothing extra. Write raw LaTeX.

**Finding "problematic" formulas (the second section).** Fix only syntax or spelling errors, never the physics or meaning. Typical problems:
- Unbalanced braces `{}`, `\left(` without `\right)`, or mismatched `(`/`]`. Use a quick brace/paren balance counter per formula.
- Misspelled commands such as `\frc`, `\sqrtt`, `\alpah`, `\lamda`, `\infity`, `\partail`, `\sumn`, or text words misspelled inside `\text{}`/`\mathrm{}`.
- Missing a backslash on a function or Greek letter, e.g. `sin`, `alpha` written as plain letters where the PDF shows a symbol. Be careful: this may simply be how the PDF displays it.
- Doubled sub/superscripts like `x^2^3`, or a stray `&` outside an alignment.
- For bracket fixes, follow common math convention: close with the matching bracket type and pair `\left`/`\right`.

A quick checker:
```python
cmds = set(re.findall(r'\\[A-Za-z]+', ' '.join(out)))
print(sorted(cmds))   # eyeball for misspelled commands
for i,f in enumerate(out):
    if f.count('{')!=f.count('}') or f.count('(')!=f.count(')') or f.count('\\left')!=f.count('\\right'): print(i,f[:120])
```
For each problematic formula, the original (as displayed, typo kept) stays in section 1. Its corrected version, with the same cleanup rules applied, goes in section 2. Do not add "fixes" for formulas that are fine.

**Output format (exact):**
```
$$f1$$
$$f2$$
...
<blank line>
$$fixed_1$$
...
```
Write it with `open('/root/latex_formula_extraction.md','w').write('\n'.join(f'$${f}$$' for f in out) + '\n\n' + '\n'.join(f'$${f}$$' for f in fixed) + '\n')`.

**Step plan:**
1. `ls /root`, `pdfinfo`, and `which marker_single`. Locate the marker skill scripts with `find / -name marker_to_markdown.py 2>/dev/null | head`.
2. Run marker into `/root/marker_out` and wait for it to finish.
3. `grep -c '\$\$'` on the md. Print only the `$$` blocks, truncated, e.g. `python - <<<'...print(i, f[:150])'`.
4. Compare the count and placement with `pdftotext -layout` (look for equation-number lines with `grep -nE '\(\s*[0-9]+\s*\)\s*$'`).
5. Write the script: extract, clean, filter, check, then add fixed lines. Run it.
6. Verify the result:
   - `wc -l` and `head` on the output.
   - Every line in the first section starts with `$$` and ends with `$$`.
   - No trailing `,` or `.`, no `\tag`, no `(n)`.
   - Exactly one blank-line separator before the fixed section.
