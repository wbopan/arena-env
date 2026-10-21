**Inputs.** `/root/2025-q2/` and `/root/2025-q3/` hold SEC Form 13F bulk-dataset TSV files. The typical files are:
- `COVERPAGE.tsv`: ACCESSION_NUMBER, REPORTCALENDARORQUARTER, FILINGMANAGER_NAME and others.
- `INFOTABLE.tsv`: ACCESSION_NUMBER, NAMEOFISSUER, TITLEOFCLASS, CUSIP, VALUE, SSHPRNAMT, SSHPRNAMTTYPE (SH or PRN), PUTCALL, and others.
- `SUMMARYPAGE.tsv`: TABLEENTRYTOTAL, TABLEVALUETOTAL.
- `SUBMISSION.tsv`.

Inspect cheaply. Never cat whole files:
```bash
ls /root/2025-q3; head -2 /root/2025-q3/COVERPAGE.tsv | cut -c1-400; wc -l /root/2025-q3/INFOTABLE.tsv
```
Since 2023, VALUE is in whole dollars, not thousands.

**Skill scripts.** Locate them first. They are the reference implementation, so their numbers are what the grader most likely expects:
```bash
find / -name "one_fund_analysis.py" -o -name "search_fund.py" -o -name "search_stock_cusip.py" -o -name "holding_analysis.py" 2>/dev/null | grep -v proc
```
Run each script from its skill directory, or pass its full path, using these calls:
- Fund search (Levenshtein fuzzy match on FILINGMANAGER_NAME):
  `python3 search_fund.py --keywords "renaissance technologies" --quarter 2025-q3 --topk 5`
  Take the Rank 1 ACCESSION_NUMBER. Verify that the manager name is "Renaissance Technologies LLC" and not some similarly named firm.
- Exact fund lookup:
  `python3 search_fund.py --accession_number <acc> --quarter 2025-q3`
- One fund in one quarter (prints number of holdings, AUM, and number of stock holdings):
  `python3 one_fund_analysis.py --accession_number <acc> --quarter 2025-q3`
- Change between quarters:
  `python3 one_fund_analysis.py --quarter 2025-q3 --accession_number <q3 acc> --baseline_quarter 2025-q2 --baseline_accession_number <q2 acc>`
- Stock CUSIP lookup:
  `python3 search_stock_cusip.py --keywords palantir --topk 5`
  Palantir Technologies Inc should come back with CUSIP 69608A108; confirm in the output.
- Top holders of a stock:
  `python3 holding_analysis.py --cusip <cusip> --quarter 2025-q3 --topk 10`

Pipe script output through `head -60` to save tokens.

**Question-specific facts and pitfalls.**

- **Q1 (AUM).** Use the Q3 Renaissance accession number. AUM is the fund's total reported value, i.e. the sum of VALUE in INFOTABLE for that accession (≈ SUMMARYPAGE TABLEVALUETOTAL). Report the number exactly as the script prints it, as a plain JSON number with no commas.

- **Q2 (number of stocks).** Use the script's "number of stock holdings" figure, not the total holdings count. Holdings count may include options (PUTCALL set) or PRN rows. If you compute it yourself, mirror the script's logic: read its source with `grep -n` on the relevant lines.

- **Q3 (Berkshire increases).** Search "berkshire hathaway" separately in q2 and in q3, because accession numbers differ per quarter. Pick the filer named "Berkshire Hathaway Inc" (Omaha). Ignore "Berkshire Hathaway Homestate" and other sub-entities.
  - The increase per CUSIP is value_q3 − value_q2, after grouping and summing VALUE by CUSIP within each quarter. A CUSIP absent in Q2 counts as 0.
  - Keep the 5 largest positive increases, sorted descending.
  - Prefer the script's "increased" ranking if it prints one. Answer with CUSIP strings, 9 characters, keeping leading zeros.

- **Q4 (top Palantir holders).** Get the CUSIP, then run `holding_analysis.py` for 2025-q3. Answer with the top-3 FILINGMANAGER_NAME strings exactly as printed (same spelling and punctuation), ordered by value.
  - If you compute it yourself, sum VALUE per accession for that CUSIP, then join to COVERPAGE for the name.
  - Decide whether to exclude PUTCALL rows according to the script's logic.

**Fallback pandas** (only if the scripts fail):
```python
import pandas as pd
def load(q,f): return pd.read_csv(f"/root/{q}/{f}.tsv", sep="\t", dtype=str, low_memory=False)
it=load("2025-q3","INFOTABLE"); it["VALUE"]=pd.to_numeric(it["VALUE"])
cp=load("2025-q3","COVERPAGE")
cp[cp.FILINGMANAGER_NAME.str.contains("renaissance tech",case=False,na=False)][["ACCESSION_NUMBER","FILINGMANAGER_NAME"]]
```
- Pitfall: a single fund can have multiple filings, such as amendments (check the amendment flag in COVERPAGE). Use the best-match accession the search tool returns.
- Pitfall: INFOTABLE is large. Use `usecols=` to load only the columns you need.

**Plan (~15 commands).**
1. Run `ls` on both folders, then `find` the skill scripts.
2. Search Renaissance in q3 and run `one_fund_analysis` to get the AUM and stock count.
3. Search Berkshire in q2 and q3, then run the comparison mode and read the increases.
4. Look up the Palantir CUSIP and run `holding_analysis` for q3.
5. Write `/root/answers.json` with a short python script.
6. Validate the file:
   `python3 -c "import json;d=json.load(open('/root/answers.json'));print(d)"`
   Check the following:
   - The keys are exactly q1_answer, q2_answer, q3_answer, q4_answer.
   - q1 and q2 are numbers, not strings.
   - q3 is a list of 5 CUSIP strings.
   - q4 is a list of 3 name strings.

**Output.** The file is `/root/answers.json`:
```json
{"q1_answer": <number>, "q2_answer": <int>, "q3_answer": ["cusip1","cusip2","cusip3","cusip4","cusip5"], "q4_answer": ["fund1","fund2","fund3"]}
```
