import json
import re
from collections import deque
from pathlib import Path

R = Path('/root/work')

def reference():
    text = (R / 'problem.pddl').read_text()
    start = re.search(r'\(:init\s+\(at jet (\w+)\)', text).group(1)
    destination = re.search(r'\(:goal\s+\(and\s+\(at jet (\w+)\)', text).group(1)
    edges = re.findall(r'\(connected (\w+) (\w+)\)', text)
    required = frozenset(re.findall(r'\(serviced (\w+)\)', text))
    unserviced = frozenset(re.findall(r'\(unserviced (\w+)\)', text))
    first = (start, frozenset())
    distance, ways = {first: 0}, {first: 1}
    queue = deque([first])
    while queue:
        state = queue.popleft()
        location, done = state
        successors = [(other, done) for source, other in edges if source == location]
        if location in unserviced and location not in done:
            successors.append((location, done | {location}))
        for nxt in successors:
            if nxt not in distance:
                distance[nxt] = distance[state] + 1
                ways[nxt] = 0
                queue.append(nxt)
            if distance[nxt] == distance[state] + 1:
                ways[nxt] += ways[state]
    goals = [(s, d) for s, d in distance.items() if s[0] == destination and required <= s[1]]
    best = min(d for _, d in goals)
    return best, sum(ways[s] for s, d in goals if d == best), len(distance)

def output():
    return json.loads((R / 'service_summary.json').read_text())

def test_file_exists():
    assert (R / 'service_summary.json').is_file()

def test_schema():
    obj = output()
    assert set(obj) == {'min_steps', 'shortest_plans', 'reachable_states'}
    assert all(type(v) is int for v in obj.values())

def test_minimum_length():
    assert output()['min_steps'] == reference()[0]

def test_shortest_plan_count():
    assert output()['shortest_plans'] == reference()[1]

def test_reachable_state_count():
    assert output()['reachable_states'] == reference()[2]
