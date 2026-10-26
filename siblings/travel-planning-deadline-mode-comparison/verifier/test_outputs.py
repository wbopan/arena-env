import csv
from pathlib import Path

ROOT = Path('/root/work')
OUT = ROOT / 'modes.csv'
FIELDS = ['date', 'origin', 'destination', 'mode', 'service_id', 'cost_usd', 'duration_min']


def read(name):
    with (ROOT / name).open(newline='') as f:
        return list(csv.DictReader(f))


def expected():
    requests, roads, flights = read('requests.csv'), read('driving.csv'), read('flights.csv')
    result = []
    for req in requests:
        cap = int(req['max_minutes'])
        choices = []
        for road in roads:
            if (road['origin'], road['destination']) != (req['origin'], req['destination']):
                continue
            hours, minutes = road['duration'].split(' hours ')
            duration = 60 * int(hours) + int(minutes.split()[0])
            cost = int(road['distance'].split()[0]) * 15 // 100 + int(road['toll_usd'])
            if duration <= cap:
                choices.append((cost, duration, 'drive', 'SELF_DRIVE'))
        for flight in flights:
            if (flight['FlightDate'], flight['OriginCityName'], flight['DestCityName']) == (req['date'], req['origin'], req['destination']):
                duration = int(flight['ActualElapsedTime'])
                if duration <= cap:
                    choices.append((2 * int(flight['Price']), duration, 'flight', flight['Flight Number']))
        cost, duration, mode, service = min(choices)
        result.append({'date': req['date'], 'origin': req['origin'], 'destination': req['destination'], 'mode': mode, 'service_id': service, 'cost_usd': str(cost), 'duration_min': str(duration)})
    return result


def test_file_exists():
    assert OUT.is_file()


def test_header_and_row_count():
    with OUT.open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == FIELDS
        rows = list(reader)
    assert len(rows) == len(read('requests.csv'))
    assert all(set(row) == set(FIELDS) for row in rows)


def test_request_order_and_numeric_fields():
    rows = read('modes.csv')
    assert [(r['date'], r['origin'], r['destination']) for r in rows] == [(r['date'], r['origin'], r['destination']) for r in read('requests.csv')]
    assert all(r['mode'] in ('drive', 'flight') and r['cost_usd'].isdigit() and r['duration_min'].isdigit() for r in rows)


def test_optimal_eligible_choices():
    assert read('modes.csv') == expected()
