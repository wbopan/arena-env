1. Inspect one npz cheaply: keys, `dt`, `channels`, data shape and amplitude scale. Check whether any label-like fields exist that you could use for tuning.
2. Build an ObsPy Stream per file: 3 Traces, same station, channel codes ending in Z/N/E, `sampling_rate=1/dt`, and your own demean/std normalization.
3. Run SeisBench `PhaseNet.from_pretrained(...)` with `.classify(st, P_threshold, S_threshold)`. Convert each pick with `idx = round((peak_time - t0)/dt)`.
4. Write `/root/results.csv` with columns `file_name,phase,pick_idx` (phase P/S, integer index).
5. Validate the CSV format. If labels exist, compute F1 at ±0.1 s and tune the model and thresholds.
