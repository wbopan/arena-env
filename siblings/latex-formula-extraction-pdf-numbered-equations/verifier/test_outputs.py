import json
import re
from pathlib import Path

from pypdf import PdfReader

WORK = Path("/root/work")
PDF = WORK / "tech_note.pdf"
OUT = WORK / "equations.json"


def norm(s):
    return " ".join(s.split())


def expected():
    res = []
    reader = PdfReader(str(PDF))
    for i, page in enumerate(reader.pages):
        for raw in (page.extract_text() or "").split("\n"):
            line = raw.rstrip()
            m = re.search(r"\((\d+)\)$", line)
            if not m:
                continue
            head = line[:m.start()]
            if not head.strip() or not head[-1].isspace():
                continue
            latex = norm(head)
            while latex and latex[-1] in ",.":
                latex = latex[:-1].rstrip()
            res.append({"number": int(m.group(1)), "page": i + 1, "latex": latex})
    return sorted(res, key=lambda d: d["number"])


def load():
    return json.loads(OUT.read_text())


def test_output_is_json_list():
    assert OUT.is_file()
    data = load()
    assert isinstance(data, list) and data


def test_schema():
    for d in load():
        assert isinstance(d, dict)
        assert set(d.keys()) == {"number", "page", "latex"}, d
        assert isinstance(d["number"], int) and isinstance(d["page"], int)
        assert isinstance(d["latex"], str)


def test_numbers_sorted_and_complete():
    got = [d["number"] for d in load()]
    assert got == [d["number"] for d in expected()]


def test_pages():
    got = [(d["number"], d["page"]) for d in load()]
    assert got == [(d["number"], d["page"]) for d in expected()]


def test_latex_text():
    got = [norm(d["latex"]) for d in load()]
    assert got == [d["latex"] for d in expected()]
