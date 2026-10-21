import csv
import random

random.seed(20240607)

CB = [
    ('P1_POWER', 'PWR-001', 'Output voltage out of range', 'vout|overvoltage|undervoltage|3v3|5v', ''),
    ('P1_POWER', 'PWR-002', 'Open or short circuit', 'os|open|short', 'ICT'),
    ('P1_POWER', 'PWR-003', 'Cold solder joint', 'solder|cold|joint|xuhan', ''),
    ('P1_POWER', 'PWR-004', 'Fixture contact failure', 'fixture|pogo|pin|contact|retest', 'ICT|FCT'),
    ('P1_POWER', 'PWR-005', 'Thermal shutdown in burn in', 'thermal|hot|temp|shutdown', 'BURNIN'),
    ('P1_POWER', 'PWR-006', 'Inductor damaged', 'inductor|coil|l1|crack', ''),
    ('P2_CTRL', 'CTL-101', 'Firmware boot failure', 'boot|fw|firmware|hang', 'BOOT|FCT'),
    ('P2_CTRL', 'CTL-102', 'UART communication error', 'uart|comm|tx|rx|baud', ''),
    ('P2_CTRL', 'CTL-103', 'Crystal oscillator not starting', 'crystal|xtal|osc|clock', ''),
    ('P2_CTRL', 'CTL-104', 'Open or short circuit', 'os|open|short', 'ICT'),
    ('P2_CTRL', 'CTL-105', 'Connector misaligned', 'connector|conn|mating|bent|pin', ''),
    ('P2_CTRL', 'CTL-106', 'EEPROM checksum mismatch', 'eeprom|checksum|crc|nvm', 'FCT|BOOT'),
]
STATIONS = {'P1_POWER': ['ICT', 'FCT', 'BURNIN'], 'P2_CTRL': ['ICT', 'FCT', 'BOOT']}
NOISE = ['ng', 'fail', 'chk', 'again', 'maybe', 'pls', 'see', 'log', 'unit', 'x2', 'ok']
DELIMS = [' / ', '; ', ' + ', ', ', '/', '+']


def make_segment(pid):
    if random.random() < 0.15:
        return ' '.join(random.sample(NOISE, random.randint(1, 3)))
    row = random.choice([r for r in CB if r[0] == pid])
    pool = row[3].split('|') + row[2].lower().split()
    k = random.randint(1, 3)
    words = random.sample(pool, min(k, len(pool)))
    words += random.sample(NOISE, random.randint(0, 2))
    random.shuffle(words)
    words = [w.upper() if random.random() < 0.3 else w for w in words]
    return ' '.join(words)


with open('codebook.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['product_id', 'code', 'standard_label', 'keywords', 'station_scope'])
    for r in CB:
        w.writerow(list(r))

with open('logs.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['record_id', 'product_id', 'station', 'raw_reason_text'])
    for i in range(1, 51):
        pid = random.choice(list(STATIONS))
        st = random.choice(STATIONS[pid])
        nseg = random.choice([1, 1, 2, 2, 3])
        text = ''
        for j in range(nseg):
            if j:
                text += random.choice(DELIMS)
            text += make_segment(pid)
        if random.random() < 0.1:
            text += ' /'
        w.writerow(['R%03d' % i, pid, st, text])
