1. Inspect with `head`/`wc` plus a numpy one-liner: span, cadence, flag counts (keep flag==0). Check whether lightkurve/transitleastsquares/astropy import.
2. Make a lightkurve LightCurve, `flatten(window_length≈0.5–1 day in cadences, odd)`, and clip upper outliers only, so dips are kept.
3. Run TLS with flux_err over 0.5 to span/2, then refine ±2% with oversampling. Cross-check with astropy BLS and check the P/2 and 2P aliases.
4. Write `f"{P:.5f}"` to `/root/period.txt` and `cat` it to verify there is a single number.
