import os
import re

from pypdf import PdfReader

WORK = "/root/work"
INP = os.path.join(WORK, "register.pdf")
OUT = os.path.join(WORK, "register_redacted.pdf")
ACCT = re.compile(r"(?<!\d)\d{10}(?!\d)")


def norm_lines(page):
    t = page.extract_text() or ""
    return [re.sub(r"\s+", " ", l).strip() for l in t.splitlines() if l.strip()]


def mask(m):
    return "******" + m.group(0)[-4:]


def src_pages():
    return [norm_lines(p) for p in PdfReader(INP).pages]


def out_pages():
    return [norm_lines(p) for p in PdfReader(OUT).pages]


def accounts():
    accts = []
    for pg in src_pages():
        for l in pg:
            accts.extend(ACCT.findall(l))
    return accts


def test_output_valid_same_pages():
    assert os.path.isfile(OUT)
    assert len(PdfReader(OUT).pages) == len(PdfReader(INP).pages)


def test_no_full_account_numbers():
    accts = accounts()
    assert len(accts) >= 20
    text = "\n".join((p.extract_text() or "") for p in PdfReader(OUT).pages)
    compact = re.sub(r"\s", "", text)
    for a in accts:
        assert a not in text, f"account {a} still extractable"
        assert a not in compact, f"account {a} still extractable"


def test_masks_present():
    expected = sorted("******" + a[-4:] for a in accounts())
    text = "\n".join((p.extract_text() or "") for p in PdfReader(OUT).pages)
    found = sorted(re.findall(r"\*{6}\d{4}(?!\d)", text))
    assert found == expected


def test_pages_match_line_for_line():
    exp = [[ACCT.sub(mask, l) for l in pg] for pg in src_pages()]
    got = out_pages()
    assert len(got) == len(exp)
    for i, (e, g) in enumerate(zip(exp, got)):
        assert g == e, f"page {i + 1} text differs"
