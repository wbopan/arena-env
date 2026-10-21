import re
from pathlib import Path

WORK = Path("/root/work")
SRC = WORK / "paper.tex"
OUT = WORK / "display_formulas.md"


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def expected():
    text = SRC.read_text()
    text = re.sub(r"(?m)^[ \t]*%.*$", "", text)
    found = []
    pats = (
        r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}",
        r"\\\[(.*?)\\\]",
        r"\$\$(.*?)\$\$",
    )
    for pat in pats:
        for m in re.finditer(pat, text, re.S):
            found.append((m.start(), m.group(1)))
    found.sort()
    res = []
    for _, b in found:
        b = re.sub(r"\\label\{[^{}]*\}", " ", b)
        b = norm(b)
        while b and b[-1] in ",.":
            b = b[:-1].rstrip()
        res.append(b)
    return res


def agent_lines():
    return [l.strip() for l in OUT.read_text().splitlines() if l.strip()]


def test_output_exists():
    assert OUT.is_file()


def test_each_line_wrapped():
    ls = agent_lines()
    assert ls, "output is empty"
    for l in ls:
        assert l.startswith("$$") and l.endswith("$$") and len(l) > 4, l


def test_formula_count():
    exp = expected()
    assert exp
    assert len(agent_lines()) == len(exp)


def test_no_labels_or_trailing_punctuation():
    for l in agent_lines():
        inner = l[2:-2].strip()
        assert "\\label" not in inner, l
        assert not inner.endswith((",", ".")), l


def test_formulas_match_in_order():
    got = [norm(l[2:-2]) for l in agent_lines()]
    assert got == expected()
