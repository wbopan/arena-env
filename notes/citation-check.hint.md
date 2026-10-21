1. Check `/root/test.bib` cheaply (`grep -c '^@'`, `head`), and test whether bibtexparser and `api.crossref.org` are reachable.
2. Write one Python script that parses the entries and checks each DOI (404 or a mismatched title) or title (CrossRef `query.bibliographic` plus difflib ratio). Print one line per entry and flag red flags: placeholder DOIs like 10.1234, generic authors, nonexistent venues, buzzword titles.
3. Decide the fakes using the evidence plus your own knowledge of famous papers.
4. Write `{"fake_citations": sorted(cleaned_titles)}` to `/root/answer.json`, with titles stripped of `{}` and `\`.
5. Reload the JSON to verify it is sorted and clean.
