# Audit placeholders in an offer letter template

Inputs in `/root/work`:

- `offer_letter_template.docx` is a Word template with placeholders of the form `{{KEY}}`.
  - KEY consists of uppercase letters and underscores.
  - Placeholders appear in body paragraphs, in table cells (including tables nested inside cells), and in the page header and footer.
  - A single placeholder is often split across several XML runs, but never across paragraphs.
- `employee_data.json` is a flat JSON object mapping data keys to values.

The tokens `{{IF_NAME}}` and `{{END_IF_NAME}}` are conditional markers. They are not placeholders.

Write `/root/work/placeholder_audit.json` with exactly these four top-level keys:

- `placeholders`: an object keyed by placeholder KEY, with conditional markers excluded. Each value is `{"count": <int>, "locations": [...]}`.
  - `count` is the total number of occurrences in the whole document. Every occurrence counts, including repeats within one paragraph.
  - `locations` is the alphabetically sorted list of distinct places where the KEY occurs. Use these values:
    - `"body"` for top-level document paragraphs.
    - `"table"` for any table cell, at any nesting depth.
    - `"header"` for the page header.
    - `"footer"` for the page footer.
- `conditions`: an alphabetically sorted list of every NAME for which an `{{IF_NAME}}` marker appears.
- `missing_keys`: a sorted list of placeholder KEYs that are not keys of `employee_data.json`.
- `unused_keys`: a sorted list of `employee_data.json` keys that never occur as a placeholder.
