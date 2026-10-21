**Goal:** compare the old employee table in `/root/employees_backup.pdf` with the current one in `/root/employees_current.xlsx`. Write `/root/diff_report.json`:
```json
{"deleted_employees": ["EMP0000X", ...],
 "modified_employees": [{"id": "EMP0000X", "field": "<column name>", "old_value": <old>, "new_value": <new>}, ...]}
```
- Deleted means the ID is in the PDF but not in the Excel file.
- Modified means the ID is in both and some field value differs. Write one entry per changed field, so one ID can have several entries.
- Sort `deleted_employees` by ID. Sort `modified_employees` by ID, then by field (stable).
- Salary, Years and Score values must be JSON numbers. Use int when the value is whole, float otherwise. Text fields stay strings.
- The "field" value must be the exact column header text, e.g. "Salary".
- New IDs that appear only in the Excel file are not requested. Do not add extra keys.

**Tools**
- PDF: use `pdfplumber`. Call `page.extract_tables()` on every page.
- The table probably spans many pages. The header row may repeat on each page or appear only on page 1, so skip any row whose first cell equals the header's first cell.
- If `extract_tables()` returns nothing, fall back to `page.extract_text()` and split the lines. As a last resort run `pdftotext -layout`.
- Excel: use `pandas.read_excel(path, dtype=str)` so IDs and numbers come in as raw strings. Convert them yourself, the same way for both sources.

**Cheap inspection (don't print whole files)**
```bash
python3 -c "import pdfplumber;p=pdfplumber.open('/root/employees_backup.pdf');print(len(p.pages));t=p.pages[0].extract_tables();print(len(t),t[0][:3] if t else p.pages[0].extract_text()[:500])"
python3 -c "import pandas as pd;x=pd.read_excel('/root/employees_current.xlsx',sheet_name=None);[print(k,v.shape,list(v.columns),v.head(3).to_dict('records')) for k,v in x.items()]"
```
Check these four things:
- Whether the column names match between the two sources.
- How many sheets the Excel file has.
- Whether PDF cells contain `$`, commas, `\n` or trailing spaces.
- Whether the last page's table is extracted correctly.

**Pitfalls**
- Normalize every cell before comparing:
  - Strip whitespace.
  - Replace `\n` with a space.
  - For numeric columns, remove `$` and `,`, then parse to float. Compare with a tolerance like `abs(a-b)>1e-9`.
  - Make "50020" and "50020.0" compare equal.
- Normalize IDs with `.strip()`.
- Header names may differ slightly in case or spacing. Map PDF headers to Excel headers through a stripped, lowercase key, and report the Excel or PDF header name (they should match).
- Drop empty or None rows from the PDF extraction.
- A row split across pages can produce partial rows. Check that the PDF row count is plausible by comparing its unique IDs with the Excel count.
- Text comparisons are exact after stripping. Do not lowercase values; a case change is a real modification.
- Date-like columns: when read as str, pandas may render them as "2020-01-01 00:00:00". Compare against the PDF's text. If formats differ, normalize both with `pd.to_datetime(...).strftime('%Y-%m-%d')`, but only when the column really is a date.

**Script (/root/diff.py)**
```python
import pdfplumber, pandas as pd, json
NUM={'salary','years','score'}
rows=[];hdr=None
with pdfplumber.open('/root/employees_backup.pdf') as pdf:
    for pg in pdf.pages:
        for t in pg.extract_tables():
            for r in t:
                r=[(c or '').replace('\n',' ').strip() for c in r]
                if not any(r): continue
                if hdr is None: hdr=r; continue
                if r[0]==hdr[0]: continue
                rows.append(r)
old=pd.DataFrame(rows,columns=hdr)
new=pd.read_excel('/root/employees_current.xlsx',dtype=str).fillna('')
new.columns=[c.strip() for c in new.columns]
idc=hdr[0]  # verify this is the ID column
def num(v):
    v=str(v).replace('$','').replace(',','').strip()
    f=float(v); return int(f) if f.is_integer() else f
def norm(col,v):
    v=str(v).strip()
    if col.strip().lower() in NUM and v!='':
        try: return num(v)
        except: return v
    return v
O={r[idc].strip():r for _,r in old.iterrows()}
N={r[idc].strip():r for _,r in new.iterrows()}
deleted=sorted(set(O)-set(N))
cmap={c.lower():c for c in new.columns}
mods=[]
for i in sorted(set(O)&set(N)):
    for c in hdr:
        if c==idc or c.lower() not in cmap: continue
        a,b=norm(c,O[i][c]),norm(c,N[i][cmap[c.lower()]])
        if a!=b: mods.append({"id":i,"field":c,"old_value":a,"new_value":b})
json.dump({"deleted_employees":deleted,"modified_employees":mods},open('/root/diff_report.json','w'),indent=2)
print(len(O),len(N),len(deleted),len(mods)); print(mods[:10])
```
Numbers are compared after conversion, so 50020 vs 50020.0 is fine because int and float compare equal in Python.

**Verification**
- Print the counts: PDF rows, Excel rows, deleted, modified. Also print `len(set(O)-set(N))` and `len(set(N)-set(O))`.
- The PDF ID count should equal the Excel count plus deleted minus added.
- If the modified list is huge, the cause is almost always normalization, not real changes. Look at a few entries:
  - A float precision difference means you should round.
  - Whitespace or line wrapping means you should collapse spaces with `' '.join(v.split())`.
  - Mismatched header names need fixing in the column map.
- Confirm all IDs match the `EMP\d{5}` pattern, so none were lost or mangled in extraction.
- Confirm numeric fields are JSON numbers, not quoted strings: `python3 -c "import json;d=json.load(open('/root/diff_report.json'));print(d['deleted_employees'],len(d['modified_employees']))"`.
