#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import csv, glob, json, os, re
PRI = [["GRAND TOTAL"], ["TOTAL RM", "TOTAL: RM"], ["TOTAL AMOUNT"], ["TOTAL", "AMOUNT DUE"]]
EXC = ["SUBTOTAL", "SUB TOTAL", "TAX", "GST", "SST", "DISCOUNT", "CHANGE", "CASH"]
NUM = re.compile(r"\d{1,3}(?:,\d{3})+\.\d{2}|\d+\.\d{2}")

def find_total(lines):
    for kws in PRI:
        for i, l in enumerate(lines):
            u = l.upper()
            if any(e in u for e in EXC):
                continue
            if any(k in u for k in kws):
                nums = NUM.findall(l)
                if not nums and i + 1 < len(lines):
                    nums = NUM.findall(lines[i + 1])
                return f"{float(nums[-1].replace(',', '')):.2f}" if nums else None
    return None

out = []
for p in sorted(glob.glob("ocr/*.tsv")):
    with open(p, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    kept = [r for r in rows if r["level"] == "5" and float(r["conf"]) >= 30 and (r["text"] or "").strip()]
    g = {}
    for r in kept:
        g.setdefault((int(r["block_num"]), int(r["par_num"]), int(r["line_num"])), []).append(r)
    lines = [" ".join(r["text"].strip() for r in sorted(g[k], key=lambda r: int(r["word_num"]))) for k in sorted(g)]
    confs = [float(r["conf"]) for r in kept]
    out.append({"filename": os.path.basename(p)[:-4] + ".jpg", "total": find_total(lines),
                "word_count": len(kept), "mean_conf": round(sum(confs) / len(confs), 2) if confs else 0.0})
with open("receipt_summary.json", "w") as f:
    json.dump(out, f, indent=2)
EOF
python3 /tmp/solve.py
