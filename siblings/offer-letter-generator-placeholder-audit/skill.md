## Reference notes

Use `python-docx` (`from docx import Document`), `json`, and `re`. **Read `paragraph.text`, not individual runs**: Word can split one `{{KEY}}` across runs, but the task says it never crosses paragraphs. No document modification is needed.

```python
doc = Document("/root/work/offer_letter_template.docx")
with open("/root/work/employee_data.json", encoding="utf-8") as f:
    data = json.load(f)

token_re = re.compile(r"\{\{([A-Z_]+)\}\}")
# For each paragraph, use token_re.finditer(paragraph.text).
# Each match is one occurrence, even when a KEY repeats in that paragraph.
```

Traverse these containers separately so each match gets the right location:

- `doc.paragraphs` → `"body"`; `doc.tables` → `"table"`.
- For every `section in doc.sections`, inspect `section.header` and `section.footer`: their `.paragraphs` → `"header"` or `"footer"`, and their `.tables` → `"table"`.
- For a table, iterate `table.rows`, then `row.cells`; inspect each `cell.paragraphs` and **recurse through `cell.tables`** to any depth. If merged cells expose the same underlying cell more than once, avoid counting that cell twice. Likewise, avoid recounting a header/footer part shared by multiple sections.

For each regex match, treat `IF_NAME` and `END_IF_NAME` as markers rather than data placeholders: collect `NAME` from opening `IF_` markers into a set; exclude both marker forms from placeholder counts. Maintain a count per remaining KEY and a set of its location strings. Convert location sets and condition names to sorted lists. Set differences give `missing_keys` (placeholder KEYs minus `data.keys()`) and `unused_keys` (`data.keys()` minus placeholder KEYs); sort both.

Write the JSON with `json.dump(...)`. A quick check is to inspect the written file and confirm it has exactly the four requested top-level keys.
