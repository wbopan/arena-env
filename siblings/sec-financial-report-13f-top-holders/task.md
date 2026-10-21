# Top 13F holders of Palantir

A SEC Form 13F extract for Q3 2025 is in `/root/work/2025-q3/`. It contains two tab-separated files with a header row:

- `COVERPAGE.tsv`: one row per filing (ACCESSION_NUMBER, REPORTCALENDARORQUARTER, FILINGMANAGER_NAME, FILINGMANAGER_CITY, FORM13FFILENUMBER)
- `INFOTABLE.tsv`: one row per reported holding line (ACCESSION_NUMBER, INFOTABLE_SK, NAMEOFISSUER, TITLEOFCLASS, CUSIP, VALUE, SSHPRNAMT, SSHPRNAMTTYPE, PUTCALL, INVESTMENTDISCRETION). VALUE is in US dollars.

The target stock is the single CUSIP whose NAMEOFISSUER contains "palantir" (case-insensitive).

Conventions:
- A filer's Palantir position is the sum of VALUE over its lines for that CUSIP with SSHPRNAMTTYPE = `SH` and an empty PUTCALL (option lines do not count toward the position).
- A filing's portfolio value is the sum of VALUE over ALL of its INFOTABLE lines (every security, including options and PRN lines).
- pct_of_portfolio = 100 * position / portfolio value.

Rank filers that hold a positive Palantir position by position value descending (ties: accession number ascending) and keep the top 5.

Write `/root/work/top_holders.csv` (comma-separated, with header) with exactly these columns in order:

`rank,manager_name,accession_number,value,pct_of_portfolio`

- rank: 1 to 5
- manager_name: FILINGMANAGER_NAME from COVERPAGE
- value: integer dollars
- pct_of_portfolio: rounded to 2 decimal places

One row per filer, 5 data rows total.
