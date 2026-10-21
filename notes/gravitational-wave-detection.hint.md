1. Check pycbc and the data length with `read_frame('/root/data/PyCBC_T2_2.gwf','H1:TEST-STRAIN')`, printing only duration and sample rate.
2. Condition the data: highpass(15) → resample to 1/2048 → crop(2,2) → psd(4) → interpolate → inverse_spectrum_truncation(4*sr, low_frequency_cutoff=15).
3. For each approximant and each m1>=m2 in 10..40, run `get_td_waveform(f_lower=20)` → resize → `cyclic_time_shift(hp.start_time)` → `matched_filter(low_frequency_cutoff=20)` → `crop(8,4)` → take max |SNR|. Use try/except and a multiprocessing Pool, run in the background with nohup, and log progress.
4. Write `/root/detection_results.csv` with header `approximant,snr,total_mass` and 3 rows (total_mass = m1+m2), then `cat` it to verify.
