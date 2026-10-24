## Reference notes

Use the Python standard library (`csv`, `datetime`, `math`). **Do not use GaMMA**: its `association()` clusters picks and estimates new events, whereas this task compares each pick with an existing candidate catalog. Waveform and phase-picking libraries are unnecessary.

- Read the three CSVs with `csv.DictReader`; numeric fields arrive as strings. Match `picks.station_id` to `stations.station_id` without changing identifier formatting. Ignore `prob`.
- Parse event `time` and pick `timestamp` with `datetime.fromisoformat()`. Both are UTC without timezone information, so subtracting the resulting datetimes gives a `timedelta`; use `.total_seconds()` to retain millisecond precision.
- Coordinates are in km. Convert station elevation to **depth positive downward**: `station_z_km = -float(elevation_m) / 1000`. For each event–station pair, straight-line distance is `sqrt((event_x-station_x)**2 + (event_y-station_y)**2 + (event_z-station_z)**2)`. Divide by `6.0` for P or `6.0/1.75` for S to obtain travel time in seconds.
- Compare `abs((pick_time - event_time).total_seconds() - travel_time_seconds)` across **all** candidate events for each pick. Select the smallest residual only if it is `<= 1.0`; otherwise use integer `-1`. Do not filter or weight by pick probability.
- Write with `csv.writer` or `csv.DictWriter`, specifying the header exactly `pick_id,event_id`. Keep one output row per input pick and convert a selected catalog `event_id` to `int`. After writing, check the header and row count against `picks.csv`.
