1. Check the folder layout with `find /root/recordings -name 'rec_001*'`, `cat` one JSON for the fs key, and confirm 960000-byte .bin files.
2. Parse with `np.fromfile('<f4')` (I = even, Q = odd samples) and subtract the mean. Take `unwrap(angle)`, then decimate 2 kHz → 50 Hz, staged or FIR.
3. BR: 0.08–0.5 Hz Butterworth + zero-padded Welch peak. HR: notch 2·BR and 3·BR, bandpass 0.7–3.0 Hz, Welch peak, then the half-frequency harmonic check (p_sub > 0.5·p_top). Cross-check with autocorrelation.
4. Write `/root/results.csv` with header `recording_id,heart_rate_bpm,breathing_rate_bpm` and 15 rows at `.1f`. Then verify BR < HR, plausible ranges, and 16 lines.
