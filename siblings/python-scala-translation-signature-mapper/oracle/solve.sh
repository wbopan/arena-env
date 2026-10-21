#!/bin/bash
set -e
cd /root/work
cat > /tmp/solve.py << 'EOF'
import ast, json

TYPES = {"int": "Int", "float": "Double", "str": "String", "bool": "Boolean", "bytes": "Array[Byte]"}

def none(n):
    return isinstance(n, ast.Constant) and n.value is None

def conv(n):
    if none(n):
        return "Unit"
    if isinstance(n, ast.Name):
        return TYPES[n.id]
    if isinstance(n, ast.BinOp):
        x = n.right if none(n.left) else n.left
        return "Option[" + conv(x) + "]"
    b = n.value.id
    els = n.slice.elts if isinstance(n.slice, ast.Tuple) else [n.slice]
    a = [conv(e) for e in els]
    if b == "tuple":
        return "(" + ", ".join(a) + ")"
    wrap = {"list": "List", "set": "Set", "dict": "Map", "Optional": "Option"}[b]
    return wrap + "[" + ", ".join(a) + "]"

def camel(s):
    w = [p for p in s.lstrip("_").split("_") if p]
    return w[0] + "".join(p[0].upper() + p[1:] for p in w[1:])

out = []
for node in ast.parse(open("api.py").read()).body:
    if isinstance(node, ast.FunctionDef):
        ps = ", ".join(camel(a.arg) + ": " + conv(a.annotation) for a in node.args.args)
        pre = "private " if node.name.startswith("_") else ""
        out.append({"python_name": node.name, "scala_name": camel(node.name),
                    "signature": f"{pre}def {camel(node.name)}({ps}): {conv(node.returns)}"})
json.dump(out, open("signatures.json", "w"), indent=2)
EOF
python3 /tmp/solve.py
