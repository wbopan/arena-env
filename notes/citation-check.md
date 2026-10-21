**Goal.** Read `/root/test.bib`, decide which entries are fabricated, and write `/root/answer.json` in exactly this shape:
```json
{"fake_citations": ["Title A", "Title B"]}
```
- The list holds titles only, not citation keys.
- Clean each title: remove `{`, `}` and `\`, collapse whitespace, strip the ends.
- Sort the list alphabetically with Python `sorted()`.
- Real citations must not appear in the list.

**Inspect cheaply first.**
- Count entries: `grep -c '^@' /root/test.bib` and `wc -l /root/test.bib`.
- Check which parser is available: `python3 -c "import bibtexparser; print(bibtexparser.__version__)"`.
- Check network access: `curl -s -m 8 "https://api.crossref.org/works?rows=1&query.bibliographic=attention+is+all+you+need" | head -c 300`.
- Print a compact table rather than the whole file. Show one line per entry with key | type | year | journal/booktitle | doi | first author | title.

**Parsing.**
- With bibtexparser v1:
  ```python
  import bibtexparser
  db = bibtexparser.load(open('/root/test.bib'))
  entries = db.entries   # list of dicts with 'ID', 'ENTRYTYPE', 'title', ...
  ```
- With v2 the API differs: `bibtexparser.parse_string(s).entries`, and each entry exposes `.fields_dict[...]`.
- If neither works, use a regex fallback: split on `\n@`, then pull each field with
  `re.search(r'\btitle\s*=\s*[{"](.*?)[}"]\s*,?\s*\n', block, re.S | re.I)`.
  Nested braces inside titles break naive regexes, so check the result visually.
- Title cleaning:
  ```python
  def clean(t):
      return re.sub(r'\s+', ' ', t.replace('{', '').replace('}', '').replace('\\', '')).strip()
  ```

**How to detect fakes.** Combine an online check with offline heuristics.

1. **CrossRef lookup (if network is available).**
   - If the entry has a DOI, fetch `https://api.crossref.org/works/<doi>`.
     - A 404 means the DOI does not exist, a strong sign of a fake.
     - If it resolves, compare the returned `message.title[0]` with the bib title. A DOI that resolves to a different paper is also suspicious.
   - Without a DOI, query `https://api.crossref.org/works?rows=3&query.bibliographic=<title>`.
     - Compare titles using `difflib.SequenceMatcher` ratio on lowercased, alphanumeric-only strings.
     - A ratio of about 0.9 or higher means it is likely real.
     - Also check that the first author's surname and the year roughly match.
   - Practical settings: `requests.get(url, timeout=10, headers={'User-Agent':'mailto:x@y.org'})`, and sleep about 0.2 s between calls.
   - For arXiv-style entries, query `http://export.arxiv.org/api/query?search_query=ti:"..."`.
   - For biomedical entries, use PubMed esearch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<title>[Title]&retmode=json`.
   - Do not treat a missing CrossRef hit alone as proof of a fake. Classic books, old papers and conference papers (NeurIPS, ICML) are often missing or poorly indexed. Combine it with the heuristics below.

2. **Offline red flags.**
   - Placeholder DOI prefixes such as `10.1234/` or `10.0000/`, or a DOI that does not match the pattern `10.\d{4,9}/\S+`.
   - Generic or placeholder authors (Smith, Doe, Johnson only) or vague author lists.
   - Journals or venues that do not exist, or a mismatch between journal and field (for example a DOI prefix belonging to another publisher: 10.1038 is Nature, 10.1126 is Science, 10.1016 is Elsevier, 10.1145 is ACM, 10.1109 is IEEE).
   - Volume or pages implausible for the year, or a year in the future.
   - Buzzword-salad titles typical of LLM hallucination, such as "Towards Unified Quantum-Neural Frameworks for…".
   - A well-known title paired with the wrong authors or year.
   - Use your own knowledge of famous papers. Classic, recognisable works such as AlphaFold, "Attention Is All You Need" and BERT are real when their metadata is consistent.

3. **Validation checks from the skill.**
   - Required fields per type:
     - article: author, title, journal, year
     - inproceedings: author, title, booktitle, year
     - book: author/editor, title, publisher, year
   - DOI should resolve, and its metadata should match the entry.
   - Missing fields alone suggest a sloppy entry, not necessarily a fake. Weigh them with the other evidence.

**Step-by-step plan.**
1. Run `grep -c '^@'` and `head -40` on the bib to see the style, then confirm whether bibtexparser and the network are available.
2. Write `/root/check.py`:
   - parse all entries;
   - for each, print key, year, venue, DOI, first author, cleaned title;
   - run the CrossRef DOI or title lookup and print its status, best-match title and similarity score.
   - Keep output to one line per entry, truncated with `[:90]`.
3. Run it and review the table. Mark an entry fake when the DOI returns 404, the title has no close match (ratio below about 0.7) together with suspicious metadata, or there are clear placeholder signals. Use domain knowledge for borderline cases, and re-query a borderline title once with a shorter query.
4. Write the answer:
   ```python
   json.dump({"fake_citations": sorted(set(fakes))}, open('/root/answer.json', 'w'), indent=2)
   ```
   Titles must be the cleaned bib titles, not CrossRef's titles.
5. Verify the output: `python3 -c "import json;d=json.load(open('/root/answer.json'));print(len(d['fake_citations']),d)"`. Confirm the list is sorted and contains no braces or backslashes.

**Pitfalls.**
- Write titles exactly as they appear in the bib after cleaning. Do not change capitalisation or punctuation; only remove `{}` and `\`. Keep LaTeX accents consistent: `{\"u}` becomes `"u` after removing braces and backslash, so inspect any such case.
- Do not include citation keys in the list.
- Do not print the whole bib file or full API JSON; truncate output.
- If the network is down, rely on the heuristics and knowledge. Do not mark every DOI-less entry as fake.
