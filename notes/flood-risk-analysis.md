**Goal.** For April 1–7, 2025, count each station's flood days. A day is a flood day when that day's maximum gage height is at or above the station's NWS "flood stage" (the minor flood threshold). Write only stations with at least one flood day.

**Output.** Write `/root/output/flood_results.csv`.
- Header must be exactly `station_id,flood_days`.
- `station_id` is the USGS ID as an 8+ digit string. Keep leading zeros, e.g. `04119000`, never `4119000`.
- `flood_days` is an integer from 1 to 7.
- Omit stations with 0 flood days.
- Sorting by flood_days descending is good practice.
- Create the directory first: `os.makedirs('/root/output', exist_ok=True)`.

**Step 1 – Inspect inputs cheaply. Never cat whole files.**
- `ls -la /root/data /root` to see whether threshold CSVs or other files ship locally.
- `wc -l /root/data/michigan_stations.txt` and `head -40 /root/data/michigan_stations.txt`.
- `grep -v '^#' /root/data/michigan_stations.txt | head -5` to see past comment lines.
- `python -c "import pandas, dataretrieval; print('ok')"` (install with `pip install dataretrieval` if missing).

**Step 2 – Recognise the station file format.**
- **USGS RDB format:** lines starting with `#` are comments, the file is tab-separated, and the first non-comment line is the header. The header has columns like `agency_cd site_no datetime tz_cd <id>_00065 <id>_00065_cd ...`. The next line is a format row like `5s 15s 20d`; drop it.
  Read it with:
  `pd.read_csv(path, sep='\t', comment='#', dtype=str)` then `df = df[~df.iloc[:,0].str.match(r'^\d+s$')]`.
- **Other layouts:** it may be a plain list of station IDs, or a table with `site_no`, datetime, and value columns. Adapt to what `head` shows.
- **Always read IDs as strings** (`dtype=str`) so leading zeros survive.

**Step 3 – Identify the water-level column.**
- Parameter `00065` is gage height in feet. This is what you compare to the flood stage.
- Parameter `00060` is discharge in cfs. Do not compare it to stage thresholds.
- Pick the value column with `[c for c in cols if '00065' in c and '_cd' not in c]`.
- Convert it with `pd.to_numeric(..., errors='coerce')`.

**Step 4 – If the file only gives station IDs, download the data.**
```python
from dataretrieval import nwis
df, meta = nwis.get_iv(sites=sid, start='2025-04-01', end='2025-04-07', parameterCd='00065')
```
- Wrap each call in try/except and skip stations where `len(df) == 0`.
- The returned frame has a datetime index; the value column is `00065`, plus `00065_cd`.
- If the data already sits in the file, do not download it.

**Step 5 – Aggregate to daily maximum. Use max, not mean.**
- Parse the datetime column, set it as the index, and filter to 2025-04-01 through 2025-04-07 inclusive.
- Then compute `daily_max = s.resample('D').max()`.
- With multiple stations in one table: `df.groupby('site_no')` then resample each group, or `df.groupby(['site_no', df.dt.dt.date])[val].max()`.
- If the datetime is tz-aware, filter by local date strings or convert consistently.
- NaN days (no data) do not count as floods.

**Step 6 – Get flood thresholds (NWS `flood stage` column).**
- First check for a local threshold file in `/root/data`.
- Otherwise download:
```python
import urllib.request, csv, io, pandas as pd
url="https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv"
content=urllib.request.urlopen(url).read().decode('utf-8')
r=csv.reader(io.StringIO(content)); headers=next(r)
nws=pd.DataFrame([row[:len(headers)] for row in r], columns=headers)  # data rows have 44 cols vs 43 headers: truncate
nws['flood stage']=pd.to_numeric(nws['flood stage'], errors='coerce')
nws['usgs id']=nws['usgs id'].astype(str).str.strip()
th=nws[(nws['usgs id']!='')&nws['flood stage'].notna()&(nws['flood stage']!=-9999)]
thr=dict(zip(th['usgs id'], th['flood stage']))
```
- Column names are lowercase with spaces: `usgs id`, `state`, `location name`, `flood stage`, `action stage`, `moderate flood stage`, `major flood stage`.
- `-9999` means no threshold defined; exclude it.
- Skip stations that have no threshold.
- Do not use the action stage or the moderate stage as the threshold.
- Units: both values are in feet. If every day shows flooding, suspect a unit or column mix-up (e.g. discharge used instead of gage height).

**Step 7 – Count and write.**
```python
res=[]
for sid, dm in daily.items():
    if sid in thr:
        n=int((dm >= thr[sid]).sum())   # >= is the NWS convention
        if n>0: res.append((sid,n))
res.sort(key=lambda x:-x[1])
pd.DataFrame(res, columns=['station_id','flood_days']).to_csv('/root/output/flood_results.csv', index=False)
```

**Step 8 – Verify.**
- `head /root/output/flood_results.csv` and `wc -l`.
- Check the header is exact and IDs keep their leading zeros.
- Check all flood_days values are between 1 and 7 and there are no duplicate stations.
- Print a short summary, e.g. how many stations had data, thresholds, and floods, as a sanity check.
- If zero stations flood, recheck: column choice, date filter, ID string matching (zero padding), and that you used `>=`.

**Plan within ~30 commands.**
1. Spend 3–5 commands inspecting.
2. Write one script, `/root/solve.py`, with a heredoc.
3. Run it, printing counts only.
4. Inspect the output head.
5. Fix and rerun if needed.
