1. Inspect page 1 of the PDF with `pdfplumber` (`extract_tables`) and the Excel file's headers and first rows with `pandas` (`dtype=str`). Never print whole files.
2. Collect all PDF table rows, skipping repeated headers and empty rows. Key both sources by stripped ID.
3. Normalize values before comparing: strip whitespace; for Salary/Years/Score remove `$` and `,` and convert to int or float.
4. Write `/root/diff_report.json` with sorted `deleted_employees` and sorted per-field `modified_employees` entries (id, field, old_value, new_value).
5. Sanity-check the counts and a few entries; a huge diff count means a normalization bug.
