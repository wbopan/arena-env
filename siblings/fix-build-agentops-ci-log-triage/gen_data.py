import random
from datetime import datetime, timedelta

random.seed(20240501)
T = [datetime(2024, 5, 1, 12, 0, 0)]
lines = []


def emit(s=''):
    T[0] += timedelta(microseconds=random.randint(2000, 900000))
    t = T[0]
    lines.append(t.strftime('%Y-%m-%dT%H:%M:%S') + '.%06d0Z ' % t.microsecond + s)


pkgs = ['api', 'core', 'db', 'utils', 'cli']
stems = ['models', 'views', 'parser', 'cache', 'auth', 'io', 'config', 'tasks']
verbs = ['parse', 'load', 'save', 'render', 'validate', 'merge', 'fetch', 'encode']
nouns = ['user', 'order', 'token', 'config', 'row', 'payload', 'session', 'header']
mods = ['yaml', 'redis.client', 'boto3.session', 'pydantic.v1', 'sqlalchemy.orm', 'httpx', 'attr']

files = []
for p in pkgs:
    for s in random.sample(stems, 3):
        files.append(f'tests/{p}/test_{s}.py')
nodes = {}
for f in files:
    n = random.randint(3, 6)
    ids = []
    while len(ids) < n:
        nm = f'test_{random.choice(verbs)}_{random.choice(nouns)}'
        if random.random() < 0.25:
            nm += f"[{random.choice(['a', 'b', 'c'])}-{random.randint(0, 9)}]"
        if nm not in ids:
            ids.append(nm)
    nodes[f] = [f'{f}::{x}' for x in ids]

coll_err_files = random.sample(files, 3)
coll_entries = []
for i, f in enumerate(coll_err_files):
    if i < 2:
        exc = f"ModuleNotFoundError: No module named '{random.choice(mods)}'"
    else:
        p = random.choice(pkgs)
        exc = f"ImportError: cannot import name 'LegacyClient' from 'app.{p}' (/src/app/{p}.py)"
    coll_entries.append(('ERROR', f, exc))

runnable = [n for f in files if f not in coll_err_files for n in nodes[f]]
failed = random.sample(runnable, 14)
rest = [n for n in runnable if n not in failed]
setup_err = random.sample(rest, 2)


def fail_exc():
    r = random.random()
    if r < 0.40:
        a = random.randint(0, 99)
        return f'AssertionError: assert {a} == {a + random.randint(1, 5)}'
    if r < 0.55:
        return f"KeyError: '{random.choice(nouns)}_id'"
    if r < 0.67:
        return "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
    if r < 0.77:
        return f"ValueError: invalid literal for int() with base 10: '{random.choice(nouns)}'"
    if r < 0.85:
        return f"AttributeError: 'NoneType' object has no attribute '{random.choice(verbs)}'"
    if r < 0.93:
        return f"ModuleNotFoundError: No module named '{random.choice(mods)}'"
    return "requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded"


fail_map = {n: fail_exc() for n in failed}
setup_map = {n: 'ConnectionRefusedError: [Errno 111] Connection refused' for n in setup_err}

emit('##[group]Run actions/cache@v4')
emit('FAILED to restore cache: no entry for key pip-3.12-abc123')
emit('##[endgroup]')
emit('##[group]Run pip install -r requirements.txt')
for pkg in ['numpy', 'pandas', 'requests', 'pytest']:
    emit(f'Collecting {pkg}')
emit("ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.")
emit("ModuleNotFoundError: No module named 'setuptools_scm' (build isolation, ignored)")
emit('##[endgroup]')
emit('##[group]Run python -m pytest -v')
emit('=' * 29 + ' test session starts ' + '=' * 29)
emit('platform linux -- Python 3.12.3, pytest-8.2.0, pluggy-1.5.0')
total = len(runnable)
emit(f'collected {total} items / {len(coll_entries)} errors')
emit()
np_ = 0
ns = 0
for i, n in enumerate(runnable):
    if n in fail_map:
        st = 'FAILED'
    elif n in setup_map:
        st = 'ERROR'
    else:
        st = random.choice(['PASSED'] * 9 + ['SKIPPED'])
        if st == 'PASSED':
            np_ += 1
        else:
            ns += 1
    emit(f'{n} {st} [{int(100 * (i + 1) / total):3d}%]')
emit()
emit('=' * 35 + ' ERRORS ' + '=' * 35)
for kind, f, exc in coll_entries:
    emit('_' * 10 + f' ERROR collecting {f} ' + '_' * 10)
    emit(f'E   {exc}')
for n, exc in setup_map.items():
    emit('_' * 10 + f" ERROR at setup of {n.split('::')[1]} " + '_' * 10)
    emit(f'E   {exc}')
emit('=' * 34 + ' FAILURES ' + '=' * 34)
for n, exc in fail_map.items():
    nm = n.split('::')[1]
    emit('_' * 20 + f' {nm} ' + '_' * 20)
    emit(f"    def {nm.split('[')[0]}():")
    emit('E       ' + exc)
    if random.random() < 0.3:
        emit('----------------------------- Captured stdout call -----------------------------')
        emit('FAILED login attempt for user=admin - retrying: attempt 2')
    emit(f"{n.split('::')[0]}:{random.randint(5, 200)}: {exc.split(':')[0]}")
emit('=' * 27 + ' short test summary info ' + '=' * 28)
fl = [('FAILED', n, e) for n, e in fail_map.items()]
el = [('ERROR', n, e) for n, e in setup_map.items()] + coll_entries
random.shuffle(fl)
random.shuffle(el)
for k, n, e in fl + el:
    emit(f'{k} {n} - {e}')
emit(f'===== {len(fail_map)} failed, {np_} passed, {ns} skipped, {len(el)} errors in {random.uniform(5, 60):.2f}s =====')
emit('FAILED: pytest exited with code 1 - see summary above')
emit('##[error]Process completed with exit code 1.')
emit('##[endgroup]')

with open('ci_log.txt', 'w') as fh:
    fh.write('\n'.join(lines) + '\n')
