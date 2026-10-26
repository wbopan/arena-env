import re
from collections import deque
from pathlib import Path

R = Path('/root/work')

def data():
    p = (R / 'problem.pddl').read_text()
    starts = tuple(re.search(r'\(at ' + a + r' (\w+)\)', p).group(1) for a in ('jet1', 'jet2'))
    targets = tuple(re.search(r'\(target ' + a + r' (\w+)\)', p).group(1) for a in ('jet1', 'jet2'))
    edges = set(re.findall(r'\(edge (\w+) (\w+)\)', p))
    return starts, targets, edges

def lines():
    return (R / 'parking.plan').read_text().splitlines()

def optimal_distance():
    start, targets, edges = data()
    queue = deque([(start, 0)])
    visited = {start}
    while queue:
        state, depth = queue.popleft()
        if state == (None, None):
            return depth
        occupied = set(state) - {None}
        for i, current in enumerate(state):
            if current is None:
                continue
            options = [None] if current == targets[i] else []
            options += [b for a, b in edges if a == current and b not in occupied]
            for destination in options:
                new = list(state)
                new[i] = destination
                new = tuple(new)
                if new not in visited:
                    visited.add(new)
                    queue.append((new, depth + 1))
    raise AssertionError('No solution')

def test_file_exists():
    assert (R / 'parking.plan').is_file()

def test_action_syntax():
    assert lines()
    assert all(re.fullmatch(r'(?:move\(jet[12], \w+, \w+\)|park\(jet[12], \w+\))', s) for s in lines())

def test_actions_applicable():
    state, targets, edges = data()
    state = list(state)
    for line in lines():
        m = re.fullmatch(r'(move|park)\((jet[12]), (\w+)(?:, (\w+))?\)', line)
        kind, aircraft, origin, dest = m.groups()
        i = int(aircraft[-1]) - 1
        assert state[i] == origin
        if kind == 'park':
            assert dest is None and origin == targets[i]
            state[i] = None
        else:
            assert dest is not None and (origin, dest) in edges
            assert dest not in state
            state[i] = dest

def test_goal_reached():
    state, targets, edges = data()
    state = list(state)
    for line in lines():
        m = re.fullmatch(r'(move|park)\(jet([12]), (\w+)(?:, (\w+))?\)', line)
        kind, number, _, dest = m.groups()
        state[int(number) - 1] = None if kind == 'park' else dest
    assert state == [None, None]

def test_shortest_length():
    assert len(lines()) == optimal_distance()
