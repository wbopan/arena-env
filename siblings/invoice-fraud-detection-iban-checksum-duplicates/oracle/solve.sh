#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import csv
import re
from difflib import SequenceMatcher
from pypdf import PdfReader

TOK = {"limited": "ltd", "corporation": "corp", "incorporated": "inc", "company": "co"}

def norm(s):
    s = re.sub(r"[^a-z0-9\s]", "", s.lower())
    return " ".join(TOK.get(t, t) for t in s.split())

def valid(iban):
    s = iban.replace(" ", "").upper()
    s = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in s)) % 97 == 1

vendors = [(r["vendor_id"], norm(r["vendor_name"])) for r in csv.DictReader(open("vendors.csv"))]
seen = {}
out = []
for i, p in enumerate(PdfReader("invoices.pdf").pages, 1):
    t = p.extract_text()
    inv = re.search(r"Invoice No:\s*(\S+)", t).group(1)
    name = re.search(r"Vendor:[ \t]*(.+)", t).group(1).strip()
    iban = re.search(r"IBAN:[ \t]*([A-Za-z0-9 ]+)", t).group(1).strip()
    amt = float(re.search(r"Amount:\s*[A-Z]{3}\s*([\d,]+\.\d{2})", t).group(1).replace(",", ""))
    n = norm(name)
    vid = next((v for v, vn in vendors if vn == n), None)
    if vid is None:
        best, sc = None, -1
        for v, vn in vendors:
            r = SequenceMatcher(None, n, vn).ratio()
            if r > sc:
                best, sc = v, r
        vid = best if sc >= 0.85 else "UNKNOWN"
    dup = ""
    if vid != "UNKNOWN":
        k = (vid, round(amt * 100))
        if k in seen:
            dup = str(seen[k])
        else:
            seen[k] = i
    out.append([i, inv, vid, f"{amt:.2f}", "true" if valid(iban) else "false", dup])

with open("invoice_audit.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["page", "invoice_no", "vendor_id", "amount", "iban_valid", "duplicate_of"])
    w.writerows(out)
EOF
python3 /tmp/solve.py
