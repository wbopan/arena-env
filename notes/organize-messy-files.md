**Goal and output format**
- Every input file (PDF, PPTX, DOCX, and any other file) must be moved into exactly one of five folders. The folder names are exact and case-sensitive: `LLM`, `trapped_ion_and_qc`, `black_hole`, `DNA`, `music_history`.
- Create the folders inside the directory that holds the files, unless the task environment says otherwise.
- Do not rename files and do not alter their contents. Use `mv` or `shutil.move` only. Never re-save a docx/pptx through a library.
- No file may remain outside the five folders. Do not leave scratch files there: write all temporary text and logs to `/tmp`.
- Fallback rule from the task: a file that fits none of the first four subjects goes to `music_history`.

**Step 1: Locate and inspect inputs cheaply**
```bash
ls / /root /app /data 2>/dev/null | head -50
find / -name "*.pdf" -not -path "*/proc/*" 2>/dev/null | head -5   # find the source dir
D=<dir>
find $D -type f | wc -l
find $D -type f | sed 's/.*\.//' | sort | uniq -c
find $D -mindepth 1 -type d                                         # subfolders?
which pdftotext pandoc
python3 -c "import pypdf, docx, pptx" 2>&1
```
- Note any existing subdirectories, hidden files and odd extensions.
- Filenames may be arXiv IDs, so classify by content, not by name.

**Step 2: Text extraction (first pages only, to save time)**
- **PDF:** `pdftotext -l 3 file.pdf -` (poppler). Fallback: `pypdf.PdfReader(f).pages[:3]` with `.extract_text()`.
- **DOCX:** `pandoc file.docx -t plain` (from the docx skill). Alternatives: python-docx with `"\n".join(p.text for p in docx.Document(f).paragraphs)`, or unzip and strip tags from `word/document.xml`.
- **PPTX:** python-pptx:
  ```python
  " ".join(s.text_frame.text for sl in Presentation(f).slides for s in sl.shapes if s.has_text_frame)
  ```
  Fallback: unzip `ppt/slides/slide*.xml` and regex the `<a:t>` text.
- **Other files** (txt, md, etc.): read raw text.
- **Empty text:** if extraction yields nothing (scanned PDF or error), also use the filename and PDF metadata title (`pdfinfo`). Flag the file for manual review.
- Wrap each extraction in try/except so one bad file does not kill the run.

**Step 3: Keyword scoring**
Lowercase the text and count occurrences per category, using weighted, specific terms.

- **LLM:** "large language model", "language model", "llm", "gpt", "transformer", "pretrain", "fine-tun", "prompt", "token", "instruction tuning", "rlhf", "in-context", "chatgpt", "bert", "attention".
- **trapped_ion_and_qc:** "trapped ion", "ion trap", "paul trap", "qubit", "quantum comput", "quantum gate", "entangl", "fidelity", "laser cooling", "ytterbium"/"yb+", "calcium"/"ca+", "quantum error correction", "superconducting qubit".
- **black_hole:** "black hole", "event horizon", "hawking", "schwarzschild", "kerr", "accretion", "gravitational wave", "general relativity", "spacetime", "quasar", "sgr a".
- **DNA:** "dna", "nucleotide", "genome", "polymerase", "double helix", "base pair", "chromosome", "sequencing", "replication", "crispr", "gene".
- **music_history:** "music", "composer", "symphony", "opera", "baroque", "renaissance", "classical period", "jazz", "bach", "mozart", "beethoven", "melody", "musical".

Pitfalls when scoring:
- Plain "quantum" appears in black-hole papers (quantum gravity, Hawking radiation). Do not count bare "quantum". Use qubit and ion terms instead.
- "Attention" and "token" are generic, so give them low weight.
- "DNA" can appear incidentally (e.g. "DNA storage" inside a QC paper). Use the argmax of counts and then check the margin.

Assignment rule:
- Assign the category with the highest score.
- If the top score is 0, assign `music_history` (the fallback).
- If the top score is under 2× the second score, mark the file "ambiguous".

**Step 4: One script, dry run first**
Write `/tmp/sort.py`:
1. Build `{file: (category, scores, first 120 chars of text)}`.
2. Write it as JSON to `/tmp/plan.json`.
3. Print only a per-category count, plus a single line for each ambiguous or zero-text file (name, scores, snippet).
4. Do not move anything yet; keep the dry run in its own mode.

**Step 5: Review and fix ambiguous files**
- Look only at the flagged lines.
- If needed, read a title: `pdftotext -l 1 f - | head -15`.
- Apply manual overrides through a small dict in the script, e.g. `OVR={"x.pdf":"DNA"}`.

**Step 6: Execute the moves**
```python
os.makedirs(os.path.join(D, c), exist_ok=True)   # for each category c
shutil.move(src, os.path.join(D, cat, os.path.basename(src)))
```
- Only move files that are not already inside one of the five folders.
- If a filename collides between subfolders, keep the name. Each target folder is distinct, so this is only an issue when two same-named files go to the same category; handle it manually.

**Step 7: Verify**
```bash
find $D -maxdepth 1 -type f | wc -l     # must be 0
for c in LLM trapped_ion_and_qc black_hole DNA music_history; do echo $c $(ls $D/$c | wc -l); done
```
- The five counts must sum to the original file count.
- Spot-check 2–3 files per folder with `pdftotext -l 1 f - | head -5`.
- Remove any temporary files you created inside `$D`. Leave any original empty subdirectories alone unless they held files you moved; never delete input files.
