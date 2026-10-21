**Inputs.** The files live at `/root/recordings/`. Each recording may sit in its own folder (`/root/recordings/rec_001/rec_001.bin` plus `.json`) or the files may be flat. Check with `ls /root/recordings | head` and `find /root/recordings -name 'rec_001*'`. Read one sidecar with `cat` (it is small) and confirm the keys: type, carrier frequency, sample rate (likely `sample_rate_hz`), sample count, and duration. The sidecar's sample rate is authoritative. Do not infer fs from the array length.

**Parsing (CW, float32 interleaved, little-endian):**
```python
raw = np.fromfile(path, dtype='<f4')
iq = raw[0::2] + 1j*raw[1::2]
assert len(iq) == fs*duration   # 120000; file size should be 960000 bytes
```
- If you get 2× the expected length, you forgot to de-interleave.
- CW radar needs no range FFT and no range-bin selection.

**Pipeline per recording (in order):**
1. Remove clutter (DC): `iq = iq - iq.mean()`. This must happen before `np.angle`.
2. Extract phase, not magnitude: `ph = np.unwrap(np.angle(iq)); ph -= ph.mean()`.
   - If you see exact 2π jumps after unwrap, low-pass at about 10 Hz before unwrapping.
3. Decimate to about 50 Hz:
   ```python
   q = int(fs/50)
   x = decimate(ph, q, ftype='iir', zero_phase=True)
   fs2 = fs/q
   ```
   - q = 40 for 2 kHz.
   - Never design sub-Hz filters at 2 kHz; SciPy silently produces NaNs.
   - `decimate` with q=40 in a single step can be unstable for IIR. If you see NaNs or garbage, decimate in stages (e.g. q=10 then q=4) or use `ftype='fir'`.
4. Detrend if needed: `scipy.signal.detrend(x)`.
5. Apply two separate bandpasses. The supine/tilt-table defaults are:
   - BR: `butter(4,[0.08,0.5],btype='band',fs=fs2)`, then `filtfilt`.
   - HR: `butter(4,[0.7,3.0],btype='band',fs=fs2)`, then `filtfilt`. Using sos form is safer: `butter(...,output='sos')` + `sosfiltfilt`.
   - Supine subjects often breathe 5–10 bpm, so do not use a 0.1 Hz lower edge.
6. Find the peak with a zero-padded Welch PSD:
   ```python
   nper = min(len(s), int(fs2*25))
   f,p = welch(s, fs=fs2, nperseg=nper, noverlap=nper//2, nfft=8*nper, detrend='constant')
   m = (f>=lo)&(f<=hi)
   pk = f[m][np.argmax(p[m])]
   ```
7. BR = pk_br × 60.
8. For HR, notch respiration harmonics before the HR bandpass, applied to the decimated phase. Cap k at 3, because higher k can destroy HR when HR ≈ k·BR:
   ```python
   for k in (2,3):
       b,a = iirnotch(k*br_hz, Q=20, fs=fs2)
       x_n = filtfilt(b,a,x_n)
   ```
   - The skills specifically warn that for slow breathers (BR < 10 bpm), the 5th–8th BR harmonics land at 0.6–1.4 Hz and can beat the real HR peak.
   - Optionally, use a sharper HR skirt: `cheby2(8,40,[0.7,3.0],btype='band',fs=fs2,output='sos')`.
9. Always run the HR second-harmonic check:
   ```python
   fsub = pk/2
   if 0.7 <= fsub <= 3.0 and np.interp(fsub,f,p) > 0.5*np.interp(pk,f,p):
       pk = fsub
   ```
   - The threshold of 0.5 can be loosened to 0.6 for noisy radar.
   - HR = pk × 60.
10. Optionally cross-check with autocorrelation over lags in [fs2/f_hi, fs2/f_lo]: `bpm_ac = 60*fs2/lag`. If it disagrees with the PSD by more than 5 bpm, inspect that recording.
    - Harmonic-support scoring helps here: prefer HR candidates whose 2f also shows power in the unfiltered PSD. A breathing-harmonic imposter usually lacks this.

**Sanity checks before writing:**
- BR < HR in every row.
- HR is roughly 42–180 bpm, plausibly 50–90 at rest.
- BR is roughly 5–30 bpm.
- `len(find_peaks(hr_sig, distance=fs2/3.0)[0])` should be about HR × 1 min. If it is off by 2×, a harmonic error slipped through.
- Print a compact table: id, BR, HR, HR_ac, and the HR peak before and after the harmonic fix. Do not print arrays.

**Output.** Write `/root/results.csv` with this exact header:
`recording_id,heart_rate_bpm,breathing_rate_bpm`
- One row per recording, rec_001 … rec_015 in sorted order, 15 rows.
- The id is a string like `rec_001`.
- Both values are in bpm, rounded to one decimal (`f"{v:.1f}"`).
- No index column and no extra columns.
- Verify with `cat /root/results.csv` (16 lines) and `wc -l`.

**Plan:**
1. Run `ls`/`find` on the recordings folder, `cat` one JSON, and check the file size with `ls -l`.
2. Write `/root/vitals.py` implementing steps 1–9, looping over all recordings and writing the CSV.
3. Run it and review the printed summary.
4. If any recording looks implausible (NaN, BR ≥ HR, HR at a band edge, PSD/AC disagreement), look at its top 3 PSD peaks via a one-liner and adjust the notch, filter, or threshold globally. Do not hand-edit values.
5. Re-run and confirm the CSV format.
