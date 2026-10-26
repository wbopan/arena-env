import random
from pathlib import Path

random.seed(4182)
nodes = random.sample(['apron', 'bridge', 'crossing', 'east', 'fuel', 'gate', 'holding', 'inner'], 7)
p = Path('.')
p.joinpath('domain.pddl').write_text('''(define (domain ground-trace)
 (:requirements :strips :typing)
 (:types aircraft node)
 (:predicates (at ?a - aircraft ?n - node) (connected ?x - node ?y - node))
 (:action move
  :parameters (?a - aircraft ?from - node ?to - node)
  :precondition (and (at ?a ?from) (connected ?from ?to))
  :effect (and (not (at ?a ?from)) (at ?a ?to))))
''')
links = '\n  '.join(f'(connected {a} {b})' for a, b in zip(nodes, nodes[1:]))
p.joinpath('problem.pddl').write_text(f'''(define (problem taxi-trace)
 (:domain ground-trace)
 (:objects jet - aircraft {' '.join(nodes)} - node)
 (:init (at jet {nodes[0]}) {links})
 (:goal (at jet {nodes[-1]})))
''')
lines = [f'move(jet, {a}, {b})' for a, b in zip(nodes[:4], nodes[1:5])]
lines += [f'move(jet, {nodes[0]}, {nodes[5]})', f'move(jet, {nodes[4]}, {nodes[5]})']
p.joinpath('candidate.plan').write_text('\n'.join(lines) + '\n')
