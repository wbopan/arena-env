import json
import re
from collections import deque
from pathlib import Path

ROOT = Path('/root/work')
PATTERN = re.compile(r'^(drive|buy)\(truck, (\w+), (\w+)\)$')


def instance():
    text = (ROOT / 'problem.pddl').read_text().lower()
    initial = text.split('(:init', 1)[1].split('(:goal', 1)[0]
    goal = text.split('(:goal', 1)[1]
    return (set(re.findall(r'\(road (\w+) (\w+)\)', initial)),
            set(re.findall(r'\(available (\w+) (\w+)\)', initial)),
            set(re.findall(r'\(owned (\w+)\)', goal)))


def result():
    return json.loads((ROOT / 'shortest_plan.json').read_text())


def test_file_exists():
    assert (ROOT / 'shortest_plan.json').is_file()


def test_schema():
    answer = result()
    assert isinstance(answer, dict) and set(answer) == {'minimum_steps', 'actions'}
    assert type(answer['minimum_steps']) is int and answer['minimum_steps'] >= 0
    assert isinstance(answer['actions'], list)
    assert all(isinstance(a, str) and PATTERN.fullmatch(a) for a in answer['actions'])
    assert answer['minimum_steps'] == len(answer['actions'])


def test_plan_reaches_goal():
    roads, offers, goals = instance()
    here, owned = 'depot', set()
    for action in result()['actions']:
        kind, first, second = PATTERN.fullmatch(action).groups()
        if kind == 'drive':
            assert here == first and (first, second) in roads
            here = second
        else:
            assert here == second and (first, second) in offers
            assert first not in owned
            owned.add(first)
    assert goals <= owned


def test_no_shorter_plan_exists():
    roads, offers, goals = instance()
    start = ('depot', frozenset())
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (here, owned), distance = queue.popleft()
        if goals <= owned:
            assert result()['minimum_steps'] == distance
            return
        successors = [(b, owned) for a, b in roads if a == here]
        successors += [(here, owned | {g}) for g, m in offers
                       if m == here and g not in owned]
        for state in successors:
            if state not in seen:
                seen.add(state)
                queue.append((state, distance + 1))
    assert False, 'Goal is unreachable'
