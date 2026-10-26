import csv
from collections import deque
from pathlib import Path

ROOT = Path('/root/work')


def read(name):
    with (ROOT / name).open(newline='') as file:
        return list(csv.DictReader(file))


def expected():
    graph = {}
    for edge in read('lemmas.csv'):
        graph.setdefault(edge['premise'], set()).add(edge['conclusion'])
    answers = []
    for goal in read('goals.csv'):
        start, target = goal['known'], goal['target']
        distances = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in graph.get(node, ()):
                if nxt not in distances:
                    distances[nxt] = distances[node] + 1
                    queue.append(nxt)
        if target not in distances:
            answers.append((goal['goal_id'], 'missing', ''))
            continue
        paths = {start: (start,)}
        for node in sorted(distances, key=lambda x: (distances[x], x)):
            if node not in paths:
                continue
            for nxt in graph.get(node, ()):
                if distances.get(nxt) == distances[node] + 1:
                    candidate = paths[node] + (nxt,)
                    if nxt not in paths or candidate < paths[nxt]:
                        paths[nxt] = candidate
        answers.append((goal['goal_id'], 'proved', '>'.join(paths[target])))
    return answers


def test_file_exists():
    assert (ROOT / 'chains.csv').is_file()


def test_schema_and_count():
    with (ROOT / 'chains.csv').open(newline='') as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == ['goal_id', 'status', 'chain']
        rows = list(reader)
    assert len(rows) == len(read('goals.csv'))
    assert all(set(row) == {'goal_id', 'status', 'chain'} for row in rows)


def test_goal_order_and_status():
    got = read('chains.csv')
    want = expected()
    assert [(r['goal_id'], r['status']) for r in got] == [(a, b) for a, b, _ in want]


def test_shortest_lexicographic_chains():
    assert [r['chain'] for r in read('chains.csv')] == [chain for _, _, chain in expected()]
