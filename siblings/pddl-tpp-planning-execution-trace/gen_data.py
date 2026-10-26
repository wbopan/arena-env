import random
from collections import deque
from pathlib import Path

random.seed(237)
places = ['depot'] + [f'market{i}' for i in range(4)]
goods = ['goods0', 'goods1']
roads = set()
for i in range(len(places)):
    a, b = places[i], places[(i + 1) % len(places)]
    roads.update(((a, b), (b, a)))
for _ in range(4):
    roads.add(tuple(random.sample(places, 2)))
stock = {(good, random.choice(places[1:])) for good in goods}
domain = '''(define (domain small-tpp-audit)
 (:requirements :strips)
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
problem = '(define (problem audit) (:domain small-tpp-audit)\n'
problem += ' (:objects truck ' + ' '.join(places + goods) + ')\n'
problem += ' (:init ' + ' '.join(init) + ')\n'
problem += ' (:goal (and ' + ' '.join(f'(delivered {g})' for g in goods) + '))\n)\n'
Path('domain.pddl').write_text(domain + '\n')
Path('problem.pddl').write_text(problem)

def route(start, end):
    queue = deque([(start, [])])
    seen = {start}
    while queue:
        here, path = queue.popleft()
        if here == end:
            return path
        for a, b in sorted(roads):
            if a == here and b not in seen:
                seen.add(b)
                queue.append((b, path + [(a, b)]))
    raise ValueError('Disconnected graph')

lines = ['unload(truck, goods0)', 'buy(truck, goods0, depot)']
for good in goods:
    market = next(m for g, m in stock if g == good)
    lines.extend(f'drive(truck, {a}, {b})' for a, b in route('depot', market))
    lines.extend([f'buy(truck, {good}, {market})',
                  f'load(truck, {good}, {market})',
                  f'unload(truck, {good})'])
    lines.extend(f'drive(truck, {a}, {b})' for a, b in route(market, 'depot'))
    lines.append(f'unload(truck, {good})')
lines.append('unload(truck, goods1)')
Path('candidate.plan').write_text('\n'.join(lines) + '\n')
