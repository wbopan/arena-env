import glob
import json
import os
import re

WORK = "/root/work"
OUT = os.path.join(WORK, "receipt_summary.json")
PRI = [["GRAND TOTAL"], ["TOTAL RM", "TOTAL: RM"], ["TOTAL AMOUNT"], ["TOTAL", "AMOUNT DUE"]]
EXC = ["SUBTOTAL", "SUB TOTAL", "TAX", "GST", "SST", "DISCOUNT", "CHANGE", "CASH"]
NUM = re.compile(r"\d{1,3}(?:,\d{3})+\.\d{2}|\d+\.\d{2}")


def _parse(path):
    with open(path) as f:
        lines = f.read().splitlines()
    hdr = lines[0].split("\t")
    words = []
    for ln in lines[1:]:
        if not ln:
            continue
        parts = ln.split("\t")
        parts += [""] * (len(hdr) - len(parts))
        r = dict(zip(hdr, parts))
        if r["level"] != "5":
            continue
        c = float(r["conf"])
        if c < 30 or not r["text"].strip():
            continue
        words.append((int(r["block_num"]), int(r["par_num"]), int(r["line_num"]), int(r["word_num"]), r["text"].strip(), c))
    return words


def _total(text_lines):
    for kws in PRI:
        for i, l in enumerate(text_lines):
            u = l.upper()
            if any(e in u for e in EXC):
                continue
            if any(k in u for k in kws):
                nums = NUM.findall(l)
                if not nums and i + 1 < len(text_lines):
                    nums = NUM.findall(text_lines[i + 1])
                if nums:
                    return f"{float(nums[-1].replace(',', '')):.2f}"
                return None
    return None


def _expected():
    res = []
    for p in sorted(glob.glob(os.path.join(WORK, "ocr", "*.tsv"))):
        words = _parse(p)
        groups = {}
        for w in words:
            groups.setdefault(w[:3], []).append(w)
        text_lines = [" ".join(x[4] for x in sorted(groups[k], key=lambda z: z[3])) for k in sorted(groups)]
        confs = [w[5] for w in words]
        res.append({
            "filename": os.path.basename(p)[:-4] + ".jpg",
            "total": _total(text_lines),
            "word_count": len(words),
            "mean_conf": round(sum(confs) / len(confs), 2) if confs else 0.0,
        })
    return res


def _load():
    with open(OUT) as f:
        return json.load(f)


def test_output_exists_and_is_json_array():
    assert os.path.isfile(OUT)
    data = _load()
    assert isinstance(data, list)


def test_schema_and_order():
    data = _load()
    exp = _expected()
    assert len(data) == len(exp)
    for d in data:
        assert set(d.keys()) == {"filename", "total", "word_count", "mean_conf"}
    assert [d["filename"] for d in data] == [e["filename"] for e in exp]


def test_totals():
    data = _load()
    exp = _expected()
    for d, e in zip(data, exp):
        assert d["total"] == e["total"], (d["filename"], d["total"], e["total"])


def test_word_counts():
    data = _load()
    exp = _expected()
    for d, e in zip(data, exp):
        assert d["word_count"] == e["word_count"], (d["filename"], d["word_count"], e["word_count"])


def test_mean_conf():
    data = _load()
    exp = _expected()
    for d, e in zip(data, exp):
        assert abs(float(d["mean_conf"]) - e["mean_conf"]) <= 0.011, (d["filename"], d["mean_conf"], e["mean_conf"])
