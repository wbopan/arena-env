## Reference notes

- Use `pypdf` to extract the PDF’s text and `openpyxl` to read the workbook. The output is JSON, so calculate values in Python; Excel formulas and spreadsheet formatting are not needed.
- Inspect cheaply before writing the processing script: print the first PDF page’s extracted text and the `Employees` sheet’s first few rows. Confirm that PDF rows remain on one line and that the workbook headers match the stated names.

```python
from pypdf import PdfReader
from openpyxl import load_workbook

reader = PdfReader("/root/work/roster_backup.pdf")
print(reader.pages[0].extract_text()[:2000])

wb = load_workbook("/root/work/roster_current.xlsx", read_only=True, data_only=True)
ws = wb["Employees"]
for row in ws.iter_rows(min_row=1, max_row=4, values_only=True):
    print(row)
```

- Process **every** PDF page with `page.extract_text()`. Each employee line has five fields separated by ` | `. Recognize data rows by an ID such as `EMP00042` at the start; this excludes repeated titles, headers and footers. Split on `|` and strip surrounding whitespace from fields, but preserve the department’s spelling and case. Convert a PDF salary with `int(salary.replace("$", "").replace(",", ""))`; ignore the start date for these calculations. Check that each accepted row has five fields rather than silently dropping malformed rows.
- For the workbook, map column names from the header row instead of assuming column positions. Iterate data rows with `ws.iter_rows(min_row=2, values_only=True)`; use `Employee ID`, `Department` and `Annual Salary`. Salaries are integer USD. Keep employee IDs as strings for matching and flag unexpected blank or duplicate IDs rather than silently overwriting them.
- Accumulate each source separately by department: headcount adds 1 per employee row; payroll adds that row’s salary. Use the **union** of department names from both sources, sorted ascending, and default missing-source counts and payroll to zero. For each department, `payroll_change = payroll_new - payroll_old`. `transfers` counts IDs in both sources whose department strings differ; `net_headcount_change = total_new - total_old`. A transfer contributes to its old department in the PDF and its new department in the workbook.
- Write with standard-library `json.dump(...)` to `/root/work/dept_summary.json`. After running the script, read the JSON back and check its keys, department ordering, integer-valued numbers, and that the department headcounts sum to each source’s employee-row count.
