`/root/work/register.pdf` is a two-page account register produced by a records system. Each page has:
- a title line
- a column header line
- one row per customer, giving a name, a 10-digit account number, a branch code and a balance
- a footer containing an 8-digit batch number

Before the register is shared, mask every account number. Replace each 10-digit account number with six asterisks followed by its last four digits. For example, `4820019937` becomes `******9937`.

This must be a true redaction. The full original numbers must not be extractable anywhere from the output's text layer. Covering them visually is not enough.

Do not mask or change anything else. Branch codes, balances, batch numbers, names, titles and footers must stay exactly as they are, in the same order and on the same pages.

Write the result to `/root/work/register_redacted.pdf`. It must be a valid PDF with the same number of pages as the input, and its text must stay real and extractable (no rasterized pages).

The output will be checked by extracting its text page by page. Ignoring differences in whitespace, each page must read line for line exactly like the original page, except that every account number is masked.
