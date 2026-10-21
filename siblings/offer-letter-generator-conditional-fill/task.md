# Fill an offer letter template with conditional blocks

Inputs in `/root/work`:

- `offer_letter_template.docx` is a Word template containing placeholders of the form `{{KEY}}`. KEY consists of uppercase letters and underscores.
  - Placeholders occur in body paragraphs, in a table (including a table nested inside a table cell), and in the page header and footer.
  - In the underlying XML, a single placeholder may be split across several runs. A placeholder never spans paragraphs.
- `employee_data.json` is an object with two members:
  - `fields` maps each KEY to its replacement string.
  - `conditions` maps a condition NAME to `"Yes"` or `"No"`.

The body contains conditional blocks. Each block has three parts:

1. A paragraph consisting only of `{{IF_NAME}}`.
2. One or more content paragraphs.
3. A paragraph consisting only of `{{END_IF_NAME}}`.

Resolve each block as follows:

- If `conditions[NAME]` is `"Yes"`, keep the content paragraphs and delete the two marker paragraphs.
- If it is `"No"`, delete the marker paragraphs and every content paragraph between them.

Produce `/root/work/offer_letter_filled.docx` with these properties:

- Every remaining placeholder is replaced by its exact value from `fields`. Do not reformat the values.
- Conditional blocks are resolved as described above.
- All other text is unchanged.
- Each paragraph that contained placeholders reads exactly like the template paragraph, with each `{{KEY}}` substituted.
- No `{{` or `}}` remains anywhere in the document. This includes tables, nested tables, the header and the footer.
