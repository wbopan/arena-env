**Goal.** Read `/root/data/PyCBC_T2_2.gwf`, channel `H1:TEST-STRAIN`, and condition it. Then matched-filter it with time-domain templates for three approximants: `SEOBNRv4_opt`, `IMRPhenomD` and `TaylorT4`. Search mass1 and mass2 over the integers 10 to 40 inclusive. For each approximant, keep the template with the highest peak |SNR|. Write `/root/detection_results.csv` with:
- the header `approximant,snr,total_mass`
- one row per approximant (3 rows), where `total_mass = mass1 + mass2` in solar masses.

**Reading the data (PyCBC).**
```python
from pycbc.frame import read_frame
strain = read_frame('/root/data/PyCBC_T2_2.gwf', 'H1:TEST-STRAIN')
print(strain.duration, strain.sample_rate, strain.start_time)
```
Do this cheaply first in a one-liner, printing only the duration and sample rate. Do not print arrays.

**Conditioning (follow the skill's pipeline exactly; order matters).**
```python
from pycbc.filter import highpass, resample_to_delta_t, matched_filter
from pycbc.psd import interpolate, inverse_spectrum_truncation
strain = highpass(strain, 15.0)                  # high-pass FIRST
strain = resample_to_delta_t(strain, 1.0/2048)   # then resample
conditioned = strain.crop(2, 2)                  # remove filter wraparound
psd = conditioned.psd(4)                         # Welch, 4 s segments
psd = interpolate(psd, conditioned.delta_f)
psd = inverse_spectrum_truncation(psd, int(4*conditioned.sample_rate),
                                  low_frequency_cutoff=15)
```
The data must still span several 4 s segments after cropping. If the PSD call raises a "must contain at least one sample" error, the data is too short.

**Matched filtering (time domain; works for all three approximants).** `SEOBNRv4_opt` is typically not available in the frequency domain, so use `get_td_waveform` for every approximant for consistency.
```python
from pycbc.waveform import get_td_waveform
import numpy as np
def peak(apx, m1, m2):
    hp, _ = get_td_waveform(approximant=apx, mass1=m1, mass2=m2,
                            delta_t=conditioned.delta_t, f_lower=20)
    hp.resize(len(conditioned))
    template = hp.cyclic_time_shift(hp.start_time)   # merger to start
    snr = matched_filter(template, conditioned, psd=psd,
                         low_frequency_cutoff=20)
    snr = snr.crop(4 + 4, 4)       # PSD + template length at start, PSD at end
    return float(abs(snr).numpy().max())
```

**Pitfalls.**
- Use `abs()`, because the SNR series is complex.
- Always crop the SNR series before taking the max. Edge artifacts otherwise give fake peaks.
- `delta_t` must match the data's `delta_t` (1/2048).
- Wrap every template call in `try/except` and skip failures. TaylorT4 and other models can fail for some mass pairs.
- If a template is longer than the data, `resize` truncates it. Low-mass templates from 20 Hz last only a few seconds, so this is normally fine.

**Grid.** `m1, m2 in range(10, 41)`. Waveforms are symmetric under swapping m1 and m2, so loop over `m1 >= m2` only. That gives 496 pairs per approximant, about 1.5k in total. Record `(snr, m1, m2)` and keep the max per approximant.

**Speed.** SEOBNRv4_opt is the slowest. Use `multiprocessing.Pool` with tasks of `(apx, m1, m2)`.
- Compute `conditioned` and `psd` at module level so forked workers inherit them.
- Run the script in the background so a long job does not block the shell: `nohup python /root/run.py > /root/log.txt 2>&1 &`.
- Print progress sparsely, e.g. per approximant or every 100 templates.
- Write partial best results to disk as each approximant finishes.
- Check progress with `tail -n 5 /root/log.txt`.

**Output writing.**
```python
import csv
with open('/root/detection_results.csv','w',newline='') as f:
    w = csv.writer(f); w.writerow(['approximant','snr','total_mass'])
    for apx in ['SEOBNRv4_opt','IMRPhenomD','TaylorT4']:
        s, m1, m2 = best[apx]; w.writerow([apx, round(s,4), m1+m2])
```
- Approximant names must be exactly `SEOBNRv4_opt`, `IMRPhenomD` and `TaylorT4`.
- `snr` is a float.
- `total_mass` is an integer sum (20 to 80).
- There is no index column and no extra columns.

**Step-by-step plan.**
1. `ls -la /root/data`. Check imports with `python -c "import pycbc; print(pycbc.__version__)"`.
2. Use a one-liner to read the frame and print duration and sample rate.
3. Write `/root/run.py` with the conditioning, `peak()`, the Pool grid search, logging and the CSV writer.
4. Optionally time a single call with `peak('SEOBNRv4_opt', 30, 30)` to estimate total runtime.
5. Run the script in the background and poll the log with `tail`.
6. `cat /root/detection_results.csv`. Verify the header, 3 rows and plausible values: an SNR of a few to tens, and a total mass between 20 and 80.
7. Sanity check: the three approximants should broadly agree on total mass for a real signal. TaylorT4 has no merger/ringdown, so it may differ more.
