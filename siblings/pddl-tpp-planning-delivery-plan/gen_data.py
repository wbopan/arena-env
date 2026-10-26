import random
from pathlib import Path

random.seed(4817)
places = ['depot'] + [f'market{i}' for i in range(5)]
goods = [f'goods{i}' for i in range(3)]
roads = set()
for i in range(len(places)):
    a, b = places[i], places[(i + 1) % len(places)]
    roads.update(((a, b), (b, a)))
for _ in range(6):
    a, b = random.sample(places, 2)
    roads.add((a, b))
stock = {(g, m) for g in goods for m in random.sample(places[1:], 2)}
domain = '''(define (domain small-tpp-delivery)
 (:requirements :strips :negative-preconditions)
 (:predicates (at ?t ?l) (road ?a ?b) (stock ?g ?m)
              (purchased ?g ?m) (empty ?t) (carrying ?t ?g)
              (delivered ?g))
 (:action drive :parameters (?t ?a ?b)
  :precondition (and (at ?t ?a) (road ?a ?b))
  :effect (and (not (at ?t ?a)) (at ?t ?b)))
 (:action buy :parameters (?t ?g ?m)
  :precondition (and (at ?t ?m) (stock ?g ?m))
  :effect (purchased ?g ?m))
 (:action load :parameters (?t ?g ?m)
  :precondition (and (at ?t ?m) (purchased ?g ?m) (empty ?t))
  :effect (and (not (empty ?t)) (carrying ?t ?g)))
 (:action unload :parameters (?t ?g)
  :precondition (and (at ?t depot) (carrying ?t ?g))
  :effect (and (not (carrying ?t ?g)) (empty ?t) (delivered ?g)))
)'''
init = ['(at truck depot)', '(empty truck)']
init += [f'(road {a} {b})' for a, b in sorted(roads)]
init += [f'(stock {g} {m})' for g, m in sorted(stock)]
problem = '(define (problem deliveries) (:domain small-tpp-delivery)\n'
problem += ' (:objects truck ' + ' '.join(places + goods) + ')\n'
problem += ' (:init ' + ' '.join(init) + ')\n'
problem += ' (:goal (and ' + ' '.join(f'(delivered {g})' for g in goods) + '))\n)\n'
Path('domain.pddl').write_text(domain + '\n')
Path('problem.pddl').write_text(problem)
