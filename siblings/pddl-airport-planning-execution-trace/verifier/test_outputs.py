import csv
import re
from pathlib import Path

R = Path('/root/work')

def expected():
    text = (R / 'problem.pddl').read_text()
    start = re.search(r'\(:init\s+\(at\s+jet\s+(\w+)\)', text).group(1)
    edges = set(re.findall(r'\(connected\s+(\w+)\s+(\w+)\)', text))
    location = start
    rows = [{'step': '0', 'action': 'INIT', 'valid': 'true', 'location': location}]
    for step, action in enumerate((R / 'candidate.plan').read_text().splitlines(), 1):
        match = re.fullmatch(r'move\(jet,\s*(\w+),\s*(\w+)\)', action)
        assert match
        origin, destination = match.groups()
        valid = origin == location and (origin, destination) in edges
        if valid:
            location = destination
        rows.append({'step': str(step), 'action': action, 'valid': str(valid).lower(), 'location': location})
        if not valid:
            break
    return rows

def actual():
    with (R / 'trace.csv').open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ['step', 'action', 'valid', 'location']
        return list(reader)

def test_file_exists():
    assert (R / 'trace.csv').is_file()

def test_initial_row():
    assert actual()[0] == expected()[0]

def test_examined_actions_and_stop():
    got, want = actual(), expected()
    assert [r['step'] for r in got] == [r['step'] for r in want]
    assert [r['action'] for r in got] == [r['action'] for r in want]

def test_preconditions_and_state_updates():
    got, want = actual(), expected()
    assert [(r['valid'], r['location']) for r in got] == [(r['valid'], r['location']) for r in want]
