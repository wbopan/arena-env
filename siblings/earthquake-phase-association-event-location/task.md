# Locate associated earthquakes and estimate their origin times

Inputs in `/root/work`:

- `stations.csv` has the columns `network`, `station`, `channel`, `longitude`, `latitude`, `elevation_m` and `response`.
  - Each row is ONE channel, so a station appears once per channel.
  - The station location is identical on all of its channel rows.
- `picks.csv` has the columns `event_id`, `network`, `station`, `phase` (`P` or `S`) and `timestamp` (ISO, UTC, milliseconds).
  - The picks are already associated to events.

Conventions:

- Project longitude/latitude to local km coordinates:
  - `x = (lon - lon0) * 111.19 * cos(lat0)`
  - `y = (lat - lat0) * 111.19`
  - `lon0` and `lat0` are the means of longitude and latitude over the unique stations (each `network.station` counted once).
- All hypocentres are at a fixed depth of 10 km below sea level.
- The station depth is `-elevation_m/1000` km.
- Use a uniform velocity model: `vp = 6.0 km/s` and `vs = vp/1.75`.
- Use straight-line 3-D travel times.

Task: for each event, find the epicentre (`x`, `y`) and origin time `t0` that minimise the sum of squared residuals over all of its picks. Each pick's residual is:

`observed - (t0 + travel time)`

All picks have equal weight.

Output: write `/root/work/locations.csv` with the header:

`event_id,time,x_km,y_km,rms_s`

- Write one row per event.
- `time`: origin time in ISO format without timezone, e.g. `2019-07-04T19:00:31.250`, with millisecond precision.
- `x_km`, `y_km`: rounded to 3 decimals.
- `rms_s`: square root of the mean squared residual at the solution, in seconds, rounded to 4 decimals.
