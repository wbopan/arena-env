**Input.** `/root/data/tess_lc.txt` is a whitespace text table with 4 columns: time (MJD, days), normalized flux, quality flag, flux error. Flag 0 means good data, so keep rows with `flag == 0`. Inspect it cheaply first:
- `head -5 /root/data/tess_lc.txt; wc -l /root/data/tess_lc.txt`
- Check for comment lines (`#`). `np.loadtxt` skips `#` lines by default. For any other header, use `skiprows`.
- One-liner to get the time span, the cadence (median of `np.diff(t)`), the flag value counts, and any NaNs:
  `python -c "import numpy as np;d=np.loadtxt('/root/data/tess_lc.txt');print(d.shape,d[:,0].min(),d[:,0].max(),np.median(np.diff(d[:,0])),np.unique(d[:,2],return_counts=True),np.isnan(d).sum())"`
- Check which packages are installed: `python -c "import lightkurve, transitleastsquares, astropy"` (try each one separately if that fails).

**Preprocessing (order matters).**
1. Keep `flag==0`. Also drop non-finite time, flux or error.
2. Remove upward outliers (flares, cosmic rays) gently, with sigma of about 3–5.
   - Clipping both sides before detrending is risky. The star's variability dominates the scatter, and transits are dips.
   - Prefer clipping after detrending, upper side only, or a symmetric 5σ clip. With lightkurve: `lc.remove_outliers(sigma_upper=3, sigma_lower=20)`.
3. Detrend the stellar variability (starspot rotation).
   - With lightkurve: `lc.flatten(window_length=N)`, a Savitzky–Golay filter. N is in cadences and must be odd.
   - The window should be longer than the transit (a few hours) but shorter than the rotation timescale.
   - At 2-min cadence (720 cadences/day), N≈361–721 (0.5–1 day) is typical. At 10/30-min cadence, scale N to cover the same time span.
   - Fast rotators need shorter windows. The skill notes 300–500 is typical for TESS.
   - Without lightkurve, use `scipy.signal.savgol_filter`, or divide by a running median over ~0.5–1 d computed per data segment (split at gaps larger than ~0.5 d).
4. Optionally do a second outlier pass at sigma about 5, removing upper outliers only, so transit points are kept.

**Period search.**
- TLS (transitleastsquares) is preferred and is more sensitive. It requires flux_err:
```python
from transitleastsquares import transitleastsquares
m = transitleastsquares(t, f, e)
r = m.power(period_min=0.5, period_max=span/2, show_progress_bar=False, verbose=False, use_threads=4)
print(r.period, r.period_uncertainty, r.SDE, r.snr, r.depth, r.duration, r.T0, r.transit_count, r.distinct_transit_count)
```
- Then refine with `period_min=0.98*P, period_max=1.02*P` and `oversampling_factor=5` or higher.
- BLS fallback in astropy:
```python
from astropy.timeseries import BoxLeastSquares
bls = BoxLeastSquares(t, f, dy=e)
durs = np.linspace(0.04, 0.3, 10)
pg = bls.autopower(durs, minimum_period=0.5, maximum_period=span/2, objective='snr')  # or likelihood
i = np.argmax(pg.power); P = pg.period[i]
```
- To refine with BLS, use `bls.power(np.linspace(0.99*P, 1.01*P, 20000), durs)`.
- Validate with `bls.compute_stats(P, pg.duration[i], pg.transit_time[i])`. Look at `depth_snr` (>7 is good), `depth_odd` vs `depth_even`, and `transit_count`.
- Plain numpy, no units, is fine for BLS.

**Validation and pitfalls.**
- TLS SDE > 9 is very strong; > 6 is a candidate. SNR > 7 is reliable.
- Aliases: check P/2 and 2P.
  - If folding at 2P shows equal odd/even depths, the true period is P.
  - If TLS warns that transits fall in gaps, check 2P.
  - Compare the depth and SDE/power at each alias.
- A peak at the rotation period or its harmonics means the detrending was insufficient. Shorten the window.
- If there is no clear peak: lengthen the window, use less aggressive clipping, or widen the duration range.
- Precision: answer to 5 decimals. Refining with a dense grid matters, because the coarse grid step can exceed 1e-4 d.
- Cross-checking TLS against BLS is cheap if both are installed. They should agree to ~1e-3 d.

**Plan (about 6–10 commands).**
1. Inspect: run head, wc and the one-liner above, plus the package import check.
2. Write `/root/solve.py`:
   - load → quality mask → finite mask → lightkurve `LightCurve(time=t, flux=f, flux_err=e)` → flatten → `remove_outliers` (upper) → TLS broad search → TLS refine (or BLS dense grid).
   - Print only compact summaries: number of points kept, top period, SDE/SNR, depth, transit count, and the values at P/2 and 2P.
   - Write the file: `open('/root/period.txt','w').write(f"{P:.5f}\n")`.
   - Keep all prints short. Never print arrays.
3. Run it. If SDE is low or the peak sits at a rotation harmonic, adjust the window or clipping and rerun.
4. Verify: `cat /root/period.txt` shows one number, e.g. `2.44535`. It must be in days, have exactly 5 decimals, and have no units or extra text.

**Output.** `/root/period.txt` contains a single numeric value in days, rounded to 5 decimal places.
