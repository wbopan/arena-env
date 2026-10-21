import copy
import json
import random

random.seed(11)
T = 12
names = ['G1', 'G2', 'G3', 'G4', 'G5']
gens = {}
for n in names[:4]:
    pmin = round(random.uniform(30, 80), 1)
    pmax = round(pmin + random.uniform(120, 250), 1)
    gens[n] = {
        'power_output_minimum': pmin,
        'power_output_maximum': pmax,
        'ramp_up_limit': round(random.uniform(25, 50), 1),
        'ramp_down_limit': round(random.uniform(25, 50), 1),
        'time_up_minimum': random.randint(2, 4),
        'time_down_minimum': 2,
        'unit_on_t0': 1,
        'time_up_t0': random.randint(6, 12),
        'time_down_t0': 0,
        'power_output_t0': round(random.uniform(pmin + 20, pmax - 20), 1),
    }
gens['G3']['time_up_t0'] = 1
gens['G3']['time_up_minimum'] = 4
gens['G5'] = {
    'power_output_minimum': 40.0, 'power_output_maximum': 150.0,
    'ramp_up_limit': 30.0, 'ramp_down_limit': 30.0,
    'time_up_minimum': 4, 'time_down_minimum': 3,
    'unit_on_t0': 0, 'time_up_t0': 0, 'time_down_t0': 5, 'power_output_t0': 0.0,
}

u = {n: [1] * T for n in names}
u['G5'] = [1 if 3 <= t <= 9 else 0 for t in range(T)]
p = {}
for n in names:
    g = gens[n]
    prev = g['power_output_t0'] if g['unit_on_t0'] else None
    arr = []
    for t in range(T):
        if not u[n][t]:
            arr.append(0.0)
            prev = None
            continue
        if prev is None:
            x = g['power_output_minimum'] + 10
        else:
            x = prev + random.uniform(-0.8 * g['ramp_down_limit'], 0.8 * g['ramp_up_limit'])
        x = min(max(x, g['power_output_minimum']), g['power_output_maximum'])
        x = round(x, 1)
        arr.append(x)
        prev = x
    p[n] = arr

demand = [round(sum(p[n][t] for n in names), 1) for t in range(T)]
reserves = [round(0.7 * sum(gens[n]['power_output_maximum'] - p[n][t] for n in names if u[n][t]), 1) for t in range(T)]


def base(U, P):
    pass


def early_stop(U, P):
    for t in range(5, T):
        U['G5'][t] = 0
        P['G5'][t] = 0.0


def over_max(U, P):
    P['G1'][7] = round(gens['G1']['power_output_maximum'] + 5, 1)


def initial_violation(U, P):
    U['G3'][1] = 0
    P['G3'][1] = 0.0


def short_outage(U, P):
    U['G4'][6] = 0
    P['G4'][6] = 0.0


def ramp_jump(U, P):
    d = gens['G1']['ramp_up_limit'] + 3
    P['G1'][1] = round(P['G1'][1] + d, 1)
    P['G2'][1] = round(P['G2'][1] - d, 1)


def shift(U, P):
    P['G2'][4] = round(P['G2'][4] + 5, 1)
    P['G4'][4] = round(P['G4'][4] - 5, 1)


mods = [base, early_stop, over_max, initial_violation, short_outage, ramp_jump, shift]
random.shuffle(mods)
schedules = []
for i, m in enumerate(mods):
    U = copy.deepcopy(u)
    P = copy.deepcopy(p)
    m(U, P)
    schedules.append({'id': f'C{i + 1}', 'commitment': U, 'production_MW': P})

with open('case.json', 'w') as f:
    json.dump({'time_periods': T, 'demand': demand, 'reserves': reserves, 'thermal_generators': gens}, f, indent=1)
with open('candidates.json', 'w') as f:
    json.dump({'schedules': schedules}, f, indent=1)
