# Transit ephemeris of a planet hidden by starspot modulation

`/root/work/tess_lc.txt` is a TESS-like light curve. It has a 40-minute cadence, covers about 14 days and contains one data gap.

The file starts with one `#` header line, followed by whitespace-separated columns:

1. time (days)
2. normalized flux
3. quality flag (0 = good)
4. flux uncertainty

The star shows spot modulation of about 1-2% with a rotation period of several days. A few unflagged upward flare spikes are present. Points with a non-zero flag carry corrupted flux.

A single transiting planet is present. Its orbital period is between 1 and 5 days, and its transit duration is between 1.5 and 5 hours. Using only quality-0 data:

1. Remove the stellar variability while preserving the transit dips.
2. Search for the periodic box-shaped transit signal.
3. Determine the planet's ephemeris and depth.

Write `/root/work/transit.json` as a JSON object with these keys:

- `period_days`: orbital period in days, rounded to 5 decimals.
- `t0`: predicted mid-transit time of the first transit at or after the first quality-0 timestamp. Use the same time system as the input and round to 5 decimals.
- `depth_ppt`: transit depth in parts per thousand, rounded to 3 decimals. Compute it as (mean detrended out-of-transit flux - mean detrended in-transit flux) * 1000, where in-transit points lie within half your fitted duration of a transit centre.

Required precision: period within 0.005 d, t0 within 0.03 d, depth within 30%.

Example: `{"period_days": 2.44535, "t0": 3000.81234, "depth_ppt": 7.512}`
