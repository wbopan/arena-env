import os
import random
import xml.etree.ElementTree as ET

random.seed(4242)
mods = ['tests.test_api', 'tests.test_models', 'tests.test_cache', 'tests.test_cli',
        'tests.integration.test_db', 'tests.integration.test_queue']
verbs = ['create', 'delete', 'list', 'update', 'retry', 'flush', 'sync', 'parse']
nouns = ['user', 'order', 'job', 'token', 'row', 'batch', 'event', 'lock']

tests = []
seen = set()
for m in mods:
    n = random.randint(6, 9)
    c = 0
    while c < n:
        nm = f'test_{random.choice(verbs)}_{random.choice(nouns)}'
        if random.random() < 0.2:
            nm += f'[case{random.randint(0, 4)}]'
        if (m, nm) in seen:
            continue
        seen.add((m, nm))
        c += 1
        r = random.random()
        kind = 'stable' if r < 0.6 else 'flaky' if r < 0.82 else 'broken' if r < 0.92 else 'skippy'
        tests.append((m, nm, kind))

os.makedirs('runs', exist_ok=True)
for run in range(1, 7):
    root = ET.Element('testsuites')
    suite = ET.SubElement(root, 'testsuite', name='pytest', hostname=f'runner-{run}',
                          timestamp=f'2024-06-{run:02d}T08:00:00')
    props = ET.SubElement(suite, 'properties')
    ET.SubElement(props, 'property', name='ci_run', value=str(run))
    nt = nf = ne = nsk = 0
    total_time = 0.0
    for m, nm, kind in tests:
        if random.random() < 0.08:
            continue
        dt = random.uniform(0.001, 2.5)
        total_time += dt
        tc = ET.SubElement(suite, 'testcase', classname=m, name=nm, time=f'{dt:.3f}')
        nt += 1
        if kind == 'skippy':
            outcome = 'skip' if random.random() < 0.85 else 'pass'
        elif random.random() < 0.07:
            outcome = 'skip'
        elif kind == 'stable':
            outcome = 'pass'
        elif kind == 'flaky':
            outcome = 'fail' if random.random() < 0.35 else 'pass'
        else:
            outcome = 'fail'
        if outcome == 'fail':
            if random.random() < 0.7:
                el = ET.SubElement(tc, 'failure', message=f'AssertionError: expected {random.randint(1, 9)} got {random.randint(10, 20)}')
                el.text = f'{m.replace(".", "/")}.py:{random.randint(10, 300)}: AssertionError'
                nf += 1
            else:
                el = ET.SubElement(tc, 'error', message='failed on setup with "TimeoutError"')
                el.text = 'E   TimeoutError: fixture db_conn timed out'
                ne += 1
        elif outcome == 'skip':
            el = ET.SubElement(tc, 'skipped', type='pytest.skip', message='requires docker')
            el.text = 'Skipped: requires docker'
            nsk += 1
        if random.random() < 0.3:
            so = ET.SubElement(tc, 'system-out')
            so.text = random.choice(['retrying connection... ok', 'no failure detected in cache warmup', 'INFO worker started'])
    suite.set('tests', str(nt))
    suite.set('failures', str(nf))
    suite.set('errors', str(ne))
    suite.set('skipped', str(nsk))
    suite.set('time', f'{total_time:.3f}')
    ET.ElementTree(root).write(f'runs/run_{run:02d}.xml', encoding='utf-8', xml_declaration=True)
