#!/usr/bin/env bash
set -euo pipefail
cat > /tmp/solve_propositions.py <<'PY'
import itertools
import json
from pathlib import Path

root = Path('/root/work')
def evaluate(node, env):
    if 'var' in node:
        return env[node['var']]
    if 'not' in node:
        return not evaluate(node['not'], env)
    if 'and' in node:
        return all(evaluate(part, env) for part in node['and'])
    if 'or' in node:
        return any(evaluate(part, env) for part in node['or'])
    left, right = node['imp']
    return not evaluate(left, env) or evaluate(right, env)

answers = []
for claim in json.loads((root / 'claims.json').read_text()):
    counterexample = next((dict(zip('abcd', bits))
        for bits in itertools.product((False, True), repeat=4)
        if not evaluate(claim['formula'], dict(zip('abcd', bits)))), None)
    answers.append({'id': claim['id'], 'valid': counterexample is None,
                    'counterexample': counterexample})
(root / 'countermodels.json').write_text(json.dumps(answers, indent=2) + '\n')
PY
python3 /tmp/solve_propositions.py
