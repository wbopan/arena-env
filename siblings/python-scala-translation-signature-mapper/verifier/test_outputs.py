import ast
import json
import os

import pytest

WORK = "/root/work"
SRC = os.path.join(WORK, "api.py")
OUT = os.path.join(WORK, "signatures.json")
PRIM = {"int": "Int", "float": "Double", "str": "String",
        "bool": "Boolean", "bytes": "Array[Byte]"}


def _is_none(n):
    return isinstance(n, ast.Constant) and n.value is None


def to_scala(n):
    if _is_none(n):
        return "Unit"
    if isinstance(n, ast.Name):
        return PRIM[n.id]
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr):
        other = n.left if _is_none(n.right) else n.right
        return f"Option[{to_scala(other)}]"
    if isinstance(n, ast.Subscript):
        base = n.value.id
        args = list(n.slice.elts) if isinstance(n.slice, ast.Tuple) else [n.slice]
        a = [to_scala(x) for x in args]
        if base == "list":
            return f"List[{a[0]}]"
        if base == "set":
            return f"Set[{a[0]}]"
        if base == "dict":
            return f"Map[{a[0]}, {a[1]}]"
        if base == "tuple":
            return "(" + ", ".join(a) + ")"
        if base == "Optional":
            return f"Option[{a[0]}]"
    raise ValueError(ast.dump(n))


def camel(s):
    parts = [p for p in s.lstrip("_").split("_") if p]
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def expected():
    tree = ast.parse(open(SRC).read())
    res = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            params = ", ".join(f"{camel(a.arg)}: {to_scala(a.annotation)}" for a in node.args.args)
            priv = "private " if node.name.startswith("_") else ""
            sig = f"{priv}def {camel(node.name)}({params}): {to_scala(node.returns)}"
            res.append({"python_name": node.name, "scala_name": camel(node.name), "signature": sig})
    return res


@pytest.fixture(scope="module")
def out():
    assert os.path.exists(OUT), "signatures.json missing"
    with open(OUT) as f:
        return json.load(f)


def test_file_exists():
    assert os.path.isfile(OUT)


def test_schema(out):
    assert isinstance(out, list)
    for o in out:
        assert isinstance(o, dict)
        assert set(o.keys()) == {"python_name", "scala_name", "signature"}


def test_functions_and_order(out):
    exp = expected()
    assert [o["python_name"] for o in out] == [e["python_name"] for e in exp]


def test_scala_names(out):
    exp = expected()
    assert [o["scala_name"] for o in out] == [e["scala_name"] for e in exp]


def test_private_modifiers(out):
    exp = expected()
    assert [o["signature"].startswith("private ") for o in out] == \
        [e["signature"].startswith("private ") for e in exp]


def test_signatures(out):
    exp = expected()
    assert len(out) == len(exp)
    for o, e in zip(out, exp):
        assert o["signature"].strip() == e["signature"], (o["signature"], e["signature"])
