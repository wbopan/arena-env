import random
from pathlib import Path

random.seed(9041)
places = ['depot'] + [f'market{i}' for i in range(5)]
goods = [f'goods{i}' for i in range(3)]
roads = set()
for i in range(len(places)):
    a, b = places[i], places[(i + 1) % len(places)]
    roads.update(((a, b), (b, a)))
for _ in range(7):
    roads.add(tuple(random.sample(places, 2)))
available = {(g, m) for g in goods for m in random.sample(places[1:], 2)}
domain = '''(define (domain small-tpp-shopping)
 (:requirements :strips :negative-preconditions)
 (:predicates (at ?t ?l) (road ?a ?b) (available ?g ?m) (owned ?g))
 (:action drive :parameters (?t ?a ?b)
  :precondition (and (at ?t ?a) (road ?a ?b))
  :effect (and (not (at ?t ?a)) (at ?t ?b)))
 (:action buy :parameters (?t ?g ?m)
  :precondition (and (at ?t ?m) (available ?g ?m) (not (owned ?g)))
  :effect (owned ?g))
)'''
init = ['(at truck depot)']
init.extend(f'(road {a} {b})' for a, b in sorted(roads))
init.extend(f'(available {g} {m})' for g, m in sorted(available))
problem = '(define (problem shopping) (:domain small-tpp-shopping)\n'
problem += ' (:objects truck ' + ' '.join(places + goods) + ')\n'
problem += ' (:init ' + ' '.join(init) + ')\n'
problem += ' (:goal (and ' + ' '.join(f'(owned {g})' for g in goods) + '))\n)\n'
Path('domain.pddl').write_text(domain + '\n')
Path('problem.pddl').write_text(problem)
