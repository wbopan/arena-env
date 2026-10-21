# 13F quarter-over-quarter position changes

SEC Form 13F extracts for two quarters are in `/root/work/2025-q2/` and `/root/work/2025-q3/`. Each folder contains two tab-separated files with a header row:

- `COVERPAGE.tsv`: one row per filing (ACCESSION_NUMBER, REPORTCALENDARORQUARTER, FILINGMANAGER_NAME, FILINGMANAGER_CITY, FORM13FFILENUMBER)
- `INFOTABLE.tsv`: one row per reported holding line (ACCESSION_NUMBER, INFOTABLE_SK, NAMEOFISSUER, TITLEOFCLASS, CUSIP, VALUE, SSHPRNAMT, SSHPRNAMTTYPE, PUTCALL, INVESTMENTDISCRETION). VALUE is in US dollars.

Analyze the filer whose FILINGMANAGER_NAME is "Berkshire Hathaway Inc" (compare case-insensitively, ignoring surrounding whitespace). Its accession number differs between the two quarters.

Conventions:
- A stock holding line has SSHPRNAMTTYPE = `SH` and an empty PUTCALL. Ignore option lines (Put/Call) and principal-amount (`PRN`) lines entirely.
- A position is the sum of VALUE over all stock holding lines with the same CUSIP within one filing. CUSIPs are 9-character strings; keep leading zeros.

Write `/root/work/changes.json`, a JSON object with these keys:
- `q2_accession`, `q3_accession`: strings
- `q2_stock_value`, `q3_stock_value`: integer total dollar value of all stock positions in that filing
- `new_positions`: list of CUSIPs held in Q3 but not in Q2, sorted by Q3 value descending
- `exited_positions`: list of CUSIPs held in Q2 but not in Q3, sorted by Q2 value descending
- `top_increases`: list of the 3 CUSIPs held in both quarters with the largest positive dollar increase (Q3 value minus Q2 value), sorted by increase descending

Break any ties by CUSIP ascending.
