import csv
import random

random.seed(424242)

CODEBOOK = [
    ('P1_POWER', 'PWR-001', 'Output voltage out of range', ''),
    ('P1_POWER', 'PWR-002', 'Open or short circuit', 'ICT'),
    ('P1_POWER', 'PWR-003', 'Cold solder joint', ''),
    ('P1_POWER', 'PWR-004', 'Fixture contact failure', 'ICT|FCT'),
    ('P1_POWER', 'PWR-005', 'Thermal shutdown in burn in', 'BURNIN'),
    ('P2_CTRL', 'CTL-101', 'Firmware boot failure', 'BOOT|FCT'),
    ('P2_CTRL', 'CTL-102', 'UART communication error', ''),
    ('P2_CTRL', 'CTL-103', 'Crystal oscillator not starting', ''),
    ('P2_CTRL', 'CTL-104', 'Open or short circuit', 'ICT'),
    ('P2_CTRL', 'CTL-105', 'Connector misaligned', ''),
]
ALIASES = {
    'PWR-001': ['vout ng', 'vout out of spec', 'output voltage low', 'undervoltage'],
    'PWR-002': ['OS NG', 'open-short', 'short circuit', 'open circuit'],
    'PWR-003': ['cold solder', 'solder crack', 'bad solder joint', 'xuhan'],
    'PWR-004': ['fixture issue', 'Pogo-Pin bad', 'contact ng', 'retest ok'],
    'PWR-005': ['over temp', 'thermal trip', 'hot shutdown'],
    'CTL-101': ['boot fail', 'FW_hang', 'no.boot', 'firmware crash'],
    'CTL-102': ['UART err', 'comm fail', 'no tx', 'baud mismatch'],
    'CTL-103': ['xtal ng', 'osc not start', 'no clock', 'crystal fail'],
    'CTL-104': ['os ng', 'open short', 'short to gnd'],
    'CTL-105': ['conn bent pin', 'connector ng', 'mating issue'],
}
PROD = {c[1]: c[0] for c in CODEBOOK}
STATIONS = {'P1_POWER': ['ICT', 'FCT', 'BURNIN'], 'P2_CTRL': ['ICT', 'FCT', 'BOOT']}
NOISE = ['see attached photo', 'pending analysis', 'customer return', 'wait for fa',
         'unknown issue', 'line stop', 'check later', 'refer to mes record']
LETTERS = 'abcdefghijklmnopqrstuvwxyz'


def norm(s):
    s = s.lower()
    for ch in '-_.':
        s = s.replace(ch, ' ')
    return ' '.join(s.split())


def mutate(s, k):
    s = list(s)
    for _ in range(k):
        op = random.choice('sdi')
        i = random.randrange(len(s))
        if op == 's':
            s[i] = random.choice(LETTERS)
        elif op == 'd' and len(s) > 3:
            del s[i]
        else:
            s.insert(i, random.choice(LETTERS))
    return ''.join(s)


def style(s):
    sep = random.choice([' ', ' ', '-', '_', '  ', '.'])
    s = s.replace(' ', sep)
    c = random.random()
    if c < 0.3:
        s = s.upper()
    elif c < 0.5:
        s = s.title()
    if random.random() < 0.2:
        s = ' ' + s + ' '
    return s


with open('codebook.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['product_id', 'code', 'standard_label', 'station_scope'])
    for r in CODEBOOK:
        w.writerow(list(r))

with open('alias_table.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['product_id', 'alias', 'code'])
    for code, als in ALIASES.items():
        for a in als:
            w.writerow([PROD[code], a, code])

with open('logs.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['record_id', 'product_id', 'station', 'reason_text'])
    for i in range(1, 121):
        pid = random.choice(list(STATIONS))
        st = random.choice(STATIONS[pid])
        if random.random() < 0.12:
            text = style(random.choice(NOISE))
        else:
            code = random.choice([c for c in ALIASES if PROD[c] == pid])
            base = norm(random.choice(ALIASES[code]))
            k = random.choices([0, 1, 2, 3, 4], weights=[40, 30, 20, 6, 4])[0]
            text = style(mutate(base, k))
        w.writerow(['T%04d' % i, pid, st, text])
