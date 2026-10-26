import random
from pathlib import Path

random.seed(7206)
nodes = random.sample(['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf'], 6)
edges = {(nodes[i], nodes[(i + 1) % 6]) for i in range(6)}
edges |= {(nodes[i], nodes[(i - 1) % 6]) for i in range(6)}
extras = [(a, b) for a in nodes for b in nodes if a != b and (a, b) not in edges]
edges.update(random.sample(extras, 3))
service = random.sample(nodes, 3)
Path('domain.pddl').write_text('''(define (domain airport-service)
 (:requirements :strips :typing)
 (:types aircraft node)
 (:predicates (at ?a - aircraft ?n - node) (connected ?x - node ?y - node)
              (unserviced ?n - node) (serviced ?n - node))
 (:action move :parameters (?a - aircraft ?x - node ?y - node)
  :precondition (and (at ?a ?x) (connected ?x ?y))
  :effect (and (not (at ?a ?x)) (at ?a ?y)))
 (:action service :parameters (?a - aircraft ?n - node)
  :precondition (and (at ?a ?n) (unserviced ?n))
  :effect (and (not (unserviced ?n)) (serviced ?n))))
''')
init = '\n  '.join(f'(connected {a} {b})' for a, b in sorted(edges))
init += '\n  ' + ' '.join(f'(unserviced {n})' for n in service)
goal = ' '.join(f'(serviced {n})' for n in service)
Path('problem.pddl').write_text(f'''(define (problem service-run)
 (:domain airport-service)
 (:objects jet - aircraft {' '.join(nodes)} - node)
 (:init (at jet {nodes[0]}) {init})
 (:goal (and (at jet {nodes[4]}) {goal})))
''')
