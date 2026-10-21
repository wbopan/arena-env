**Goal and output.** Read `/root/paper1.pdf`, `/root/paper2.pdf` and `/root/paper3.pdf`. Write anonymized copies to `/root/redacted/paper1.pdf`, `/root/redacted/paper2.pdf` and `/root/redacted/paper3.pdf`, keeping the same file names. Create the folder first with `mkdir -p /root/redacted`. Each output must be a valid PDF with the same page count as its input. At least 80% of the original text must remain. The References section must stay intact, because self-citations are allowed.

**Tool: PyMuPDF (`import fitz`).** Redact only exact text matches, as true redactions, never as black boxes drawn on top:
```python
for r in page.search_for("John Smith"):
    page.add_redact_annot(r, fill=(0,0,0))
page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)  # keep figures intact
```
- `search_for` is case-insensitive and matches within a line.
- If a name or affiliation wraps onto two lines, search for each line's fragment separately.
- Never redact whole text blocks or pages.
- Never use `draw_rect`. The text stays extractable underneath, so it is not a redaction.
- Check that `pypdf` and `pdftotext` are available for cross-checking.

**What to redact (before References only).**
1. **Author names:** use full names ("Jane Q. Doe"). Never use a bare surname, which would also hit "Doe et al." elsewhere.
2. **Affiliations:** universities, labs, companies, departments, cities and addresses in the author block.
3. **Emails:** use a regex such as `[\w.+-]+@[\w-]+(\.[\w-]+)+`. Also catch brace forms like `{a,b}@x.edu`; search the whole token.
4. **Contribution footnotes:** "Equal contribution", "Correspondence to: …", "Work done while at …".
5. **arXiv identifiers:** `arXiv:\d{4}\.\d{4,5}(v\d+)?`. Also redact the full rotated margin stamp on page 1, e.g. "arXiv:2401.12345v2 [cs.LG] 3 Feb 2024". Find the exact string with `page.get_text()` and search it in parts if needed.
6. **Venue strings:** "Published as a conference paper at ICLR 2024", "Proceedings of the 41st International Conference on Machine Learning, Vienna, Austria. PMLR 235, 2024. Copyright 2024 by the author(s).", "Accepted at … Workshop", and NeurIPS/ACL/CVPR footers. These are usually headers or footers that repeat on every page, so search all pre-reference pages.
7. **DOIs:** `10\.\d{4,9}/\S+`.
8. **Identifying URLs:** personal or lab GitHub and homepage links. Redact the text and also delete the link:
   ```python
   for l in page.get_links():
       if 'github' in l.get('uri', ''):
           page.delete_link(l)
   ```
9. **Acknowledgements:** names, grant holders and institutions mentioned there. Redact only those phrases, not the whole section.

**Metadata.** Authors are often stored in the file metadata too. Before saving, clear it:
```python
doc.set_metadata({})
doc.del_xml_metadata()
```

**References boundary pitfall.** The skill's example skips every page from the first one whose text contains "references". That breaks when the word "references" appears earlier in the body text. Do this instead:
- Find the heading line itself: a line whose stripped text equals "References", "REFERENCES" or "Bibliography".
- Use `page.get_text("dict")` or `search_for("References")`, and record the page index and the heading's y-coordinate.
- On the heading page, keep only match rectangles with `r.y1 < heading_y`.
- On later pages, skip redaction entirely.

Exceptions after References:
- **Repeated footers or venue strings** (e.g. "Proceedings of …") still leak and are not citations. Redact them on all pages, as long as they are not inside a reference entry.
- **Appendices after References** may contain acknowledgements or author info. Redact those too, using the same full-phrase rule.

**Cheap inspection (don't print whole files).**
```bash
python -c "import fitz;d=fitz.open('/root/paper1.pdf');print(len(d),d.metadata);print(d[0].get_text()[:2500])"
pdftotext /root/paper1.pdf - | grep -n -iE "arxiv|@|universit|institute|inc\.|proceedings|conference|workshop|published|accepted|equal contrib|correspond|acknowledg|github|doi" | head -60
```
- Run these for each paper.
- Look at the Acknowledgements paragraph with `grep -n -A8 -i acknowledg`.
- Look at the page footers: print the last 300 characters of `d[1].get_text()`.
- Write down the exact strings as they appear in the extracted text, including ligatures and odd spacing.

**Script plan (`/root/redact.py`).**
```python
import fitz, re, os
P = {1: [...exact strings...], 2: [...], 3: [...]}
RX = [r'arXiv:\s?\d{4}\.\d{4,5}(v\d+)?(\s*\[[\w.\-]+\])?', r'[\w.+-]+@[\w-]+(\.[\w-]+)+', r'10\.\d{4,9}/\S+']
os.makedirs('/root/redacted', exist_ok=True)
for i, pats in P.items():
    doc = fitz.open(f'/root/paper{i}.pdf')
    ref_pg, ref_y = find_refs(doc)  # heading line search as above
    for pn, page in enumerate(doc):
        if ref_pg is not None and pn > ref_pg:
            continue
        txt = page.get_text()
        found = list(pats) + [m.group(0) for rx in RX for m in re.finditer(rx, txt)]
        for s in set(found):
            for r in page.search_for(s):
                if pn == ref_pg and r.y0 >= ref_y:
                    continue
                page.add_redact_annot(r, fill=(0, 0, 0))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    doc.set_metadata({}); doc.del_xml_metadata()
    doc.save(f'/root/redacted/paper{i}.pdf', garbage=3, deflate=True)
```
- Regex hits taken from extracted text may contain newlines. Split on `\n` and search each piece.
- If `search_for` returns nothing for a string, print it. That usually means a line break or ligature (e.g. "ﬁ") is in the way; search a shorter, still-unique full phrase.

**Verification (required).** For each output:
1. Page count equals the original.
2. The retained ratio `len(redacted text) / len(original text)` is at least 0.8. A ratio below 0.7 means something went badly wrong.
3. The text before References contains none of the names, affiliations, emails, `arXiv:` stamps or venue strings. Grep `pdftotext /root/redacted/paperN.pdf -` with the same pattern list.
4. The References section text is unchanged. Compare the text after the heading in the original and the redacted file.
5. `fitz.open(out).metadata` shows an empty author.

If any leak remains, add the exact string to the script and rerun. Don't edit the outputs by hand.
