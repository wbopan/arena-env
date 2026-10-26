import re
from pathlib import Path

ROOT = Path('/root/work')
LINE = re.compile(r'^([a-z]+)\(([a-z0-9]+(?:, [a-z0-9]+)*)\)$')


def instance():
    text = (ROOT / 'problem.pddl').read_text().lower()
    init = text.split('(:init', 1)[1].split('(:goal', 1)[0]
    goals = text.split('(:goal', 1)[1]
    roads = set(re.findall(r'\(road (\w+) (\w+)\)', init))
    stock = set(re.findall(r'\(stock (\w+) (\w+)\)', init))
    required = set(re.findall(r'\(delivered (\w+)\)', goals))
    return roads, stock, required


def actions():
    return (ROOT / 'delivery.plan').read_text().splitlines()


def test_file_exists():
    assert (ROOT / 'delivery.plan').is_file()


def test_line_format():
    assert actions()
    assert all(LINE.fullmatch(line) for line in actions())


def test_actions_are_applicable():
    roads, stock, _ = instance()
    location, cargo = 'depot', None
    purchased, delivered = set(), set()
    for line in actions():
        match = LINE.fullmatch(line)
        name, args = match.group(1), match.group(2).split(', ')
        if name == 'drive':
            assert len(args) == 3 and args[0] == 'truck'
            assert args[1] == location and (args[1], args[2]) in roads
            location = args[2]
        elif name == 'buy':
            assert len(args) == 3 and args[0] == 'truck'
            assert location == args[2] and (args[1], args[2]) in stock
            purchased.add((args[1], args[2]))
        elif name == 'load':
            assert len(args) == 3 and args[0] == 'truck'
            assert location == args[2] and cargo is None
            assert (args[1], args[2]) in purchased
            cargo = args[1]
        elif name == 'unload':
            assert len(args) == 2 and args[0] == 'truck'
            assert location == 'depot' and cargo == args[1]
            delivered.add(cargo)
            cargo = None
        else:
            assert False, name
    assert delivered >= instance()[2]
