# Stellar rotation periods with a Lomb-Scargle periodogram

Before transit searches, the spot-rotation signal of each target star must be characterised. The file `/root/work/stars_lc.csv` contains irregularly sampled photometry of six stars. Its columns are `star_id,time,flux,quality`. Time is in days and flux is normalised. Rows are sorted by time, so the stars are interleaved. Only rows with `quality == 0` are valid, because flagged rows contain corrupted flux.

For each star, use only its valid points and do the following:

1. Evaluate a generalized (floating-mean) Lomb-Scargle periodogram on the frequency grid f_k = 0.05 + 0.0005*k cycles/day, k = 0..3900 (0.05 to 2.0 inclusive).
   - The power at frequency f is 1 - RSS/TSS.
   - RSS is the residual sum of squares of an unweighted least-squares fit of flux = a*sin(2*pi*f*t) + b*cos(2*pi*f*t) + c, with t being the time column as given.
   - TSS is the sum of squared deviations of the flux from its mean.
2. Select the grid frequency with the highest power. The rotation period is 1/f, in days.
3. The amplitude is sqrt(a^2 + b^2) from the fit at that frequency, in fractional flux units.

Write `/root/work/rotation.csv` in this format:

- The header is exactly `star_id,period_days,amplitude`.
- Write one row per star, sorted by star_id ascending.
- `period_days` is rounded to 4 decimal places.
- `amplitude` is rounded to 5 decimal places.

Example row: `STAR01,3.1416,0.01234`
