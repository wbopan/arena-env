**Goal.** Scan `/root/package-lock.json` offline with Trivy. Keep only findings with Severity HIGH or CRITICAL. Write them to `/root/security_audit.csv` with this exact header line:
`Package,Version,CVE_ID,Severity,CVSS_Score,Fixed_Version,Title,Url`

**Step 1. Inspect cheaply (do not cat big files).**
- `which trivy; trivy --version`
- `wc -c /root/package-lock.json; head -c 400 /root/package-lock.json`
- Find the offline DB. It is `<cache-dir>/db/trivy.db` next to `metadata.json`:
  `find / -name trivy.db -not -path '/proc/*' 2>/dev/null`
  Likely places are `/root/.cache/trivy`, `/root/trivy-cache` and `./trivy-cache`.
- The `--cache-dir` value is the directory that CONTAINS `db/`, not the `db` folder itself.

**Step 2. Run Trivy offline.**
```
trivy fs /root/package-lock.json --format json --output /root/trivy_report.json \
  --scanners vuln --skip-db-update --offline-scan --cache-dir <CACHE_DIR>
```
- `--skip-db-update` is critical. Without it, Trivy tries to download the DB and fails with no network.
- On "failed to initialize DB", the cache-dir path is wrong.
- If `fs` on the single file finds nothing, retry by scanning the directory: `trivy fs /root ...`. Then keep only Results whose Target is package-lock.json.
- Do NOT pass `--severity` unless you want to. Filtering in Python is fine and transparent.

**Step 3. Understand the JSON structure.**
- Path: `data["Results"][i]["Vulnerabilities"]`. This key may be missing or null, so use `or []`.
- Fields to read from each vulnerability: `VulnerabilityID`, `PkgName`, `InstalledVersion`, `FixedVersion` (may be absent), `Severity`, `Title`, `PrimaryURL`, and `CVSS`.
- `CVSS` is a dict keyed by source (`nvd`, `ghsa`, `redhat`). Each source has `V3Score` and optionally `V2Score`.
- Quick look: `python3 -c "import json;d=json.load(open('/root/trivy_report.json'));v=[x for r in d.get('Results',[]) for x in (r.get('Vulnerabilities') or [])];print(len(v));print(json.dumps(v[0],indent=1)[:1500])"`

**CVSS score rules (from the skill).**
- Use the V3 score with priority NVD → GHSA → RedHat.
- Fall back to NVD V2 only if no V3 exists. Otherwise write `N/A`.
- Check that the score is numeric (int or float).

**Field mapping and conventions.**
| CSV column | Trivy field | Fallback |
|---|---|---|
| Package | PkgName | — |
| Version | InstalledVersion | — |
| CVE_ID | VulnerabilityID | — |
| Severity | Severity (uppercase string, e.g. CRITICAL) | — |
| CVSS_Score | number from the priority rule | `N/A` |
| Fixed_Version | FixedVersion | `N/A` |
| Title | Title | Description, else `N/A` |
| Url | PrimaryURL | first item of References, else `N/A` |

- If FixedVersion is missing or empty, write `N/A`.
- Use `N/A` for missing values, never empty strings or None.
- Filter on the Trivy `Severity` label in {HIGH, CRITICAL}.
- Deduplicate identical (Package, Version, CVE_ID) rows.
- Use `csv.DictWriter` with `newline=''` and `encoding='utf-8'`. It quotes titles containing commas automatically.
- Always write the header, even when there are zero rows.

**Step 4. Script (`/root/audit.py`).**
```python
import json, csv
d = json.load(open('/root/trivy_report.json'))
H = ["Package","Version","CVE_ID","Severity","CVSS_Score","Fixed_Version","Title","Url"]

def score(v):
    c = v.get('CVSS') or {}
    for s in ('nvd','ghsa','redhat'):
        x = (c.get(s) or {}).get('V3Score')
        if isinstance(x, (int, float)):
            return x
    x = (c.get('nvd') or {}).get('V2Score')
    return x if isinstance(x, (int, float)) else 'N/A'

rows, seen = [], set()
for r in d.get('Results') or []:
    for v in r.get('Vulnerabilities') or []:
        sev = (v.get('Severity') or '').upper()
        if sev not in ('HIGH', 'CRITICAL'):
            continue
        k = (v.get('PkgName'), v.get('InstalledVersion'), v.get('VulnerabilityID'))
        if k in seen:
            continue
        seen.add(k)
        refs = v.get('References') or []
        rows.append({
            "Package": v.get('PkgName'),
            "Version": v.get('InstalledVersion'),
            "CVE_ID": v.get('VulnerabilityID'),
            "Severity": sev,
            "CVSS_Score": score(v),
            "Fixed_Version": v.get('FixedVersion') or 'N/A',
            "Title": v.get('Title') or v.get('Description') or 'N/A',
            "Url": v.get('PrimaryURL') or (refs[0] if refs else 'N/A'),
        })

with open('/root/security_audit.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=H)
    w.writeheader()
    w.writerows(rows)
print(len(rows))
```

**Step 5. Verify.**
- `head -3 /root/security_audit.csv; wc -l /root/security_audit.csv`
- Confirm the header matches exactly.
- Confirm Severity values are only HIGH or CRITICAL: `cut -d, -f4 ... | sort | uniq -c`. Titles may contain commas, so a Python `csv` count is the safer check.
- Confirm there are no empty cells; `N/A` should be used instead.
- Compare the row count with the number of HIGH/CRITICAL findings in the Trivy JSON.

**Pitfalls.**
- Do not invent CVEs or scores. Use only what Trivy's DB reports.
- Some IDs may be GHSA-* rather than CVE-*. Keep them as Trivy reports them.
- Multiple installed versions of the same package give separate rows.
- Do not print the whole lockfile or the whole report.
