1. Run `marker_single latex_paper.pdf --output_format markdown --disable_image_extraction --output_dir /root/marker_out` (long timeout), then grep the md for `$$` blocks. Ignore inline `$`.
2. Join each block into one line and strip `\tag{}`, `(n)` equation numbers and trailing `,`/`.`/`;`. Keep the content verbatim, and cross-check the count against `pdftotext -layout`.
3. Scan for misspelled commands and unbalanced braces/brackets or `\left`/`\right`.
4. Write `/root/latex_formula_extraction.md` with one `$$f$$` per line, a blank line, then the fixed versions, and verify it with `head`/`wc -l`.
