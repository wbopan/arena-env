import ast
import csv
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'target_shortlist.csv'


def expected():
    counts = {}
    for path in (ROOT / 'tests').glob('test_*.py'):
        tree = ast.parse(path.read_text())
        imports = {}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('pkg.'):
                for alias in node.names:
                    imports[alias.asname or alias.name] = node.module.split('.')[-1] + '.' + alias.name
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_'):
                called = {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
                for name in called & imports.keys():
                    key = imports[name]
                    counts[key] = counts.get(key, 0) + 1
    rows = []
    for path in (ROOT / 'pkg').glob('*.py'):
        for node in ast.parse(path.read_text()).body:
            if not isinstance(node, ast.FunctionDef) or node.name.startswith('_'):
                continue
            key = path.stem + '.' + node.name
            args = [a.arg for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs]
            score = 3 * any(word in node.name for word in ('parse', 'decode', 'load', 'validate')) + 2 * any(a in ('data', 'payload', 'text', 'raw') for a in args) - 2 * counts.get(key, 0)
            rows.append((key, score, counts.get(key, 0)))
    return sorted(rows, key=lambda row: (-row[1], row[0]))[:3]


def read():
    with OUT.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def test_file_exists():
    assert OUT.is_file()


def test_schema_and_count():
    fields, rows = read()
    assert fields == ['qualname', 'score', 'test_functions']
    assert len(rows) == 3
    assert all(set(row) == set(fields) for row in rows)


def test_ranked_targets():
    _, rows = read()
    assert [r['qualname'] for r in rows] == [r[0] for r in expected()]


def test_scores_and_test_counts():
    _, rows = read()
    assert [(int(r['score']), int(r['test_functions'])) for r in rows] == [(r[1], r[2]) for r in expected()]
