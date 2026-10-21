Before redacting three draft papers for blind review, I need an inventory of every identity leak they contain. The inputs are `/root/work/paper1.pdf`, `/root/work/paper2.pdf` and `/root/work/paper3.pdf`.

Every PDF uses the same layout:
- Page 1, line 1 is the title.
- Line 2 is the author list. Names are `First Last` and are separated by `, `. Each name is followed by affiliation markers in square brackets, e.g. `Alice Wong [1,2]`.
- Next come affiliation lines of the form `[k] Institution Name`, up to the line that reads exactly `Abstract`.
- A line that reads exactly `References` starts the bibliography. Entries look like `[n] Surname, F.; Surname, F. (YYYY). Title. Venue.`
- The bibliography and anything after it (such as an appendix) are out of scope for leak detection.

For each paper, compute the following from the text that comes before the `References` line:
- `authors`: the full author names (`First Last`), in listed order.
- `affiliations`: the institution names, ordered by marker number.
- `emails`: every email address, lowercased, unique, sorted ascending.
- `arxiv_ids`: every arXiv identifier written as `arXiv:YYMM.NNNNN`. Give the bare id (no `arXiv:` prefix, no `vN` version suffix), unique, sorted ascending.

Also compute `self_citations`, which uses the bibliography. It is the ascending list of entry numbers `n` (integers) whose author list contains a paper author written as `Surname, F.`, where F is that author's first initial. An entry with the same surname but a different initial is not a self-citation.

Write `/root/work/leaks.json` as a single object keyed by file name:
`{"paper1.pdf": {"authors": [...], "affiliations": [...], "emails": [...], "arxiv_ids": [...], "self_citations": [...]}, "paper2.pdf": {...}, "paper3.pdf": {...}}`
