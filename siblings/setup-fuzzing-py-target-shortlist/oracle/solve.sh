#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_targets.py <<'PY'
import ast
import csv
from collections import defaultdict
from pathlib import Path

root = Path('/root/work')
coverage = defaultdict(int)
for file in (root / 'tests').glob('*.py'):
    tree = ast.parse(file.read_text())
    bindings = {}
    for statement in tree.body:
        if isinstance(statement, ast.ImportFrom) and statement.module and statement.module.startswith('pkg.'):
            for item in statement.names:
                bindings[item.asname or item.name] = statement.module.rsplit('.', 1)[-1] + '.' + item.name
    for test in tree.body:
        if isinstance(test, ast.FunctionDef) and test.name.startswith('test_'):
            used = {n.func.id for n in ast.walk(test) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            for symbol in used:
                if symbol in bindings:
                    coverage[bindings[symbol]] += 1

candidates = []
for file in (root / 'pkg').glob('*.py'):
    for function in ast.parse(file.read_text()).body:
        if not isinstance(function, ast.FunctionDef) or function.name.startswith('_'):
            continue
        qualname = f'{file.stem}.{function.name}'
        parameters = function.args.posonlyargs + function.args.args + function.args.kwonlyargs
        name_points = 3 if any(x in function.name for x in ('parse', 'decode', 'load', 'validate')) else 0
        arg_points = 2 if any(p.arg in ('data', 'payload', 'text', 'raw') for p in parameters) else 0
        candidates.append((qualname, name_points + arg_points - 2 * coverage[qualname], coverage[qualname]))
candidates.sort(key=lambda row: (-row[1], row[0]))
with (root / 'target_shortlist.csv').open('w', newline='', encoding='utf-8') as output:
    writer = csv.writer(output)
    writer.writerow(['qualname', 'score', 'test_functions'])
    writer.writerows(candidates[:3])
PY
python3 /tmp/solve_targets.py
