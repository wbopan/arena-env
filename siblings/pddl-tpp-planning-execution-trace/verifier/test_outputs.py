import csv
import re
from pathlib import Path

ROOT = Path('/root/work')
FIELDS = ['step', 'action', 'applicable', 'location', 'cargo', 'delivered', 'goal_after']
PATTERN = re.compile(r'^([a-z]+)\(truck, (\w+)(?:, (\w+))?\)$')


def inputs():
    text = (ROOT / 'problem.pddl').read_text().lower()
    initial, goal = text.split('(:init', 1)[1].split('(:goal', 1)
    roads = set(re.findall(r'\(road (\w+) (\w+)\)', initial))
    stock = set(re.findall(r'\(stock (\w+) (\w+)\)', initial))
    goals = set(re.findall(r'\(delivered (\w+)\)', goal))
    return roads, stock, goals, (ROOT / 'candidate.plan').read_text().splitlines()


def rows():
    with (ROOT / 'execution_trace.csv').open(newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == FIELDS
        return list(reader)


def expected():
    roads, stock, goals, lines = inputs()
    here, cargo = 'depot', None
    purchased, delivered = set(), set()
    output = []
    for number, line in enumerate(lines, 1):
        match = PATTERN.fullmatch(line)
        assert match is not None
        name, first, second = match.groups()
        if name == 'drive':
            valid = second is not None and here == first and (first, second) in roads
            if valid:
                here = second
        elif name == 'buy':
            valid = second is not None and here == second and (first, second) in stock
            if valid:
                purchased.add((first, second))
        elif name == 'load':
            valid = (second is not None and here == second and cargo is None
                     and (first, second) in purchased)
            if valid:
                cargo = first
        elif name == 'unload':
            valid = second is None and here == 'depot' and cargo == first
            if valid:
                delivered.add(first)
                cargo = None
        else:
            raise AssertionError(name)
        output.append({'step': str(number), 'action': line,
                       'applicable': str(int(valid)), 'location': here,
                       'cargo': cargo if cargo is not None else '-',
                       'delivered': ';'.join(sorted(delivered)) or '-',
                       'goal_after': str(int(goals <= delivered))})
    return output


def test_file_exists():
    assert (ROOT / 'execution_trace.csv').is_file()


def test_row_count_and_actions():
    actual = rows()
    lines = inputs()[3]
    assert len(actual) == len(lines)
    assert [(row['step'], row['action']) for row in actual] == [
        (str(i), line) for i, line in enumerate(lines, 1)]


def test_applicability_flags():
    assert [row['applicable'] for row in rows()] == [
        row['applicable'] for row in expected()]


def test_resulting_states_and_goals():
    for actual, reference in zip(rows(), expected()):
        for field in ('location', 'cargo', 'delivered', 'goal_after'):
            assert actual[field] == reference[field]
