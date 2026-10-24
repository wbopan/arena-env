## Reference notes

Use `python-docx` (`from docx import Document`) and standard-library `json` and `re`. Load `employee_data.json` as an object with separate `fields` and `conditions` mappings.

**Resolve conditional blocks before field replacement.** Markers are *entire body paragraphs*, not text surrounding content in one paragraph. Work from `list(doc.paragraphs)` so deletion does not disrupt iteration. Pair paragraphs matching `r'\{\{IF_([A-Z_]+)\}\}'` and `r'\{\{END_IF_([A-Z_]+)\}\}'` by name. For `"Yes"`, delete only the two marker paragraphs; for `"No"`, also delete the intervening content paragraphs. To delete a paragraph:

```python
element = paragraph._element
element.getparent().remove(element)
```

**Replace at paragraph level, never by searching each run separately.** Word may distribute one `{{KEY}}` across several runs, while `paragraph.text` presents the complete text. Match field placeholders with `r'\{\{([A-Z_]+)\}\}'`; substitute from `fields`, not `conditions`. One straightforward text-preserving approach is to compute the fully substituted paragraph text, assign it to the first run, and clear subsequent runs. This preserves the paragraph’s text but can change character-level formatting, so use run-offset-aware editing if retaining that formatting matters. Do not replace conditional markers as fields.

**Visit every story location.** `doc.paragraphs` excludes table cells, headers, and footers. Recurse through tables because cells may contain nested tables:

```python
def visit_table(table, visit_paragraph):
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                visit_paragraph(paragraph)
            for nested in cell.tables:
                visit_table(nested, visit_paragraph)
```

Apply the paragraph visitor to `doc.paragraphs` and `doc.tables`; then, for each `section in doc.sections`, visit `section.header.paragraphs`, `section.footer.paragraphs`, and any tables in those headers and footers. Save with `doc.save(output_path)`.

Before finishing, reopen the saved DOCX and inspect text in those same locations for `{{` or `}}`. Also compare affected paragraph text against substitution of its original full paragraph text, rather than against individual runs.
