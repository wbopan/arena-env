1. For each `/root/paperN.pdf`, print only page 1 text (`[:2500]`) and grep `pdftotext` output for arxiv, @, universit, proceedings, conference, published, equal contrib, acknowledg and github, to collect exact identifying strings.
2. Write one PyMuPDF script: `search_for` exact full strings plus regex (arXiv/email/DOI) → `add_redact_annot` → `apply_redactions`, only above the "References" heading line.
3. Also clear metadata, then save to `/root/redacted/paperN.pdf`.
4. Verify: same page count, ≥80% text retained, no leaks in the pre-References text, References unchanged.
