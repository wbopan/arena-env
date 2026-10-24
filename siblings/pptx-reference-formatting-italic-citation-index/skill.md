## Reference notes

Use **python-pptx** (`from pptx import Presentation`) to inspect runs and placeholders. Plain-text extraction loses the run-level formatting needed here; no PPTX editing is required.

```python
prs = Presentation("/root/work/slides.pptx")
for slide_no, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:  # shape-tree order
        if shape.is_placeholder or not shape.has_text_frame:
            continue
        paragraphs = shape.text_frame.paragraphs
        runs = [run for p in paragraphs for run in p.runs]
        if not any(run.text.strip() for run in runs):
            continue
        if any(run.font.italic is not True
               for run in runs if run.text.strip()):
            continue
        text = " ".join("".join(run.text for run in p.runs)
                        for p in paragraphs)
        # normalize text before indexing
```

- `run.font.italic` can be `True`, `False`, or `None`. **Only `True` qualifies** for a non-whitespace run; inherited italic formatting (`None`) does not. Ignore whitespace-only runs when checking formatting, but retain their text during concatenation.
- Normalize the assembled text with `re.sub(r"\s+", " ", text).strip()`. Joining runs with spaces would incorrectly insert spaces *within* a paragraph.
- If a slide contains group shapes, inspect their child `shape.shapes` in order, recursively, to preserve shape-tree order.
- Use normalized text’s `.casefold()` as the deduplication key. Keep the first occurrence’s normalized text as the title. Traverse slides and shapes in order; collect 1-based slide numbers in sets, then write each as `sorted(...)`.
- Write JSON with the standard-library `json` module, using exactly the top-level `references` list and each entry’s `number`, `title`, and `slides` fields. After writing, reopen the JSON to check its structure and inspect a few extracted titles and slide lists.
