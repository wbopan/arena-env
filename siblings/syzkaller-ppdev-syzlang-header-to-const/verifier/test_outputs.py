import os
import re

W = "/root/work"
OUT = os.path.join(W, "dev_zq.txt.const")
SZ = {"char": 1, "unsigned char": 1, "short": 2, "unsigned short": 2, "int": 4,
      "unsigned int": 4, "long": 8, "unsigned long": 8, "long long": 8}


def expected():
    txt = open(os.path.join(W, "zq.h")).read()
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    structs = {}
    for m in re.finditer(r"struct\s+(\w+)\s*\{(.*?)\};", txt, re.S):
        off, al = 0, 1
        for decl in m.group(2).split(";"):
            decl = decl.strip()
            if not decl:
                continue
            t = " ".join(decl.split()[:-1])
            s = SZ[t]
            off = (off + s - 1) // s * s + s
            al = max(al, s)
        structs[m.group(1)] = (off + al - 1) // al * al
    defs = {}
    for m in re.finditer(r"^#define[ \t]+(\w+)[ \t]+([^\n]+?)[ \t]*$", txt, re.M):
        defs[m.group(1)] = m.group(2)
    chars = {k: ord(v[1]) for k, v in defs.items() if re.fullmatch(r"'.'", v)}
    res = {}
    for k, v in defs.items():
        if k in chars:
            continue
        m = re.fullmatch(r"_IO(R|W|WR)?\(\s*([^,]+?)\s*,\s*(\w+)\s*(?:,\s*(.+?)\s*)?\)", v)
        if m:
            tch = m.group(2)
            t = ord(tch[1]) if tch.startswith("'") else chars[tch]
            nr = int(m.group(3), 0)
            d = {None: 0, "W": 1, "R": 2, "WR": 3}[m.group(1)]
            size = 0
            if m.group(4):
                a = m.group(4)
                size = structs[a.split()[1]] if a.startswith("struct ") else SZ[" ".join(a.split())]
            res[k] = (d << 30) | (size << 16) | (t << 8) | nr
            continue
        m = re.fullmatch(r"\(\s*1\s*<<\s*(\d+)\s*\)", v)
        if m:
            res[k] = 1 << int(m.group(1))
            continue
        res[k] = int(v, 0)
    return res


def read_out():
    assert os.path.exists(OUT), "output file missing"
    lines = [l.strip() for l in open(OUT).read().splitlines() if l.strip()]
    return lines


def parse_pairs(lines):
    pairs = []
    for l in lines[1:]:
        m = re.fullmatch(r"(\w+)\s*=\s*(\d+)", l)
        assert m, f"bad line: {l!r}"
        pairs.append((m.group(1), int(m.group(2))))
    return pairs


def test_file_exists():
    assert os.path.exists(OUT)


def test_arches_line():
    lines = read_out()
    assert lines, "empty file"
    assert re.fullmatch(r"arches\s*=\s*amd64", lines[0]), lines[0]


def test_names_match():
    pairs = parse_pairs(read_out())
    names = [p[0] for p in pairs]
    assert len(names) == len(set(names)), "duplicate names"
    assert set(names) == set(expected().keys())


def test_values_correct():
    exp = expected()
    got = dict(parse_pairs(read_out()))
    wrong = {k: (got.get(k), v) for k, v in exp.items() if got.get(k) != v}
    assert not wrong, f"wrong values (got, expected): {wrong}"


def test_sorted():
    names = [p[0] for p in parse_pairs(read_out())]
    assert names == sorted(names)
