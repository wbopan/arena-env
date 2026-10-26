import random
from pathlib import Path

random.seed(3947)
nodes = random.sample(['apron', 'bay', 'cross', 'dock', 'east', 'fuel', 'gate'], 7)
edges = {(nodes[i], nodes[(i + 1) % 7]) for i in range(7)}
edges |= {(nodes[i], nodes[(i - 1) % 7]) for i in range(7)}
remaining = [(a, b) for a in nodes for b in nodes if a != b and (a, b) not in edges]
edges.update(random.sample(remaining, 3))
Path('domain.pddl').write_text('''(define (domain two-aircraft-parking)
 (:requirements :strips :typing)
 (:types aircraft node)
 (:predicates (at ?a - aircraft ?n - node) (edge ?x - node ?y - node)
              (clear ?n - node) (target ?a - aircraft ?n - node)
              (parked ?a - aircraft))
 (:action move :parameters (?a - aircraft ?x - node ?y - node)
  :precondition (and (at ?a ?x) (edge ?x ?y) (clear ?y))
  :effect (and (not (at ?a ?x)) (not (clear ?y)) (at ?a ?y) (clear ?x)))
 (:action park :parameters (?a - aircraft ?n - node)
  :precondition (and (at ?a ?n) (target ?a ?n))
  :effect (and (not (at ?a ?n)) (clear ?n) (parked ?a))))
''')
initial = ['(at jet1 ' + nodes[0] + ')', '(at jet2 ' + nodes[2] + ')']
initial += [f'(clear {n})' for i, n in enumerate(nodes) if i not in (0, 2)]
initial += [f'(edge {a} {b})' for a, b in sorted(edges)]
initial += [f'(target jet1 {nodes[4]})', f'(target jet2 {nodes[6]})']
Path('problem.pddl').write_text('''(define (problem parking-run)
 (:domain two-aircraft-parking)
 (:objects jet1 jet2 - aircraft ''' + ' '.join(nodes) + ''' - node)
 (:init ''' + ' '.join(initial) + ''')
 (:goal (and (parked jet1) (parked jet2))))
''')
