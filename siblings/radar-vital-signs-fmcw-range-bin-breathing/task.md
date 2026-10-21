# FMCW subject localisation and breathing rate

Four short 60 GHz FMCW radar captures of a person lying in front of the radar are in `/root/work/`. Each capture `cap_NN` (NN = 01..04) has two files:

- `cap_NN.bin` is raw ADC data stored as little-endian int16 interleaved complex values (I then Q). Multiply by the sidecar `scale_factor` to get volts. There is one chirp per frame. The data is frame-major: frame 0's `samples_per_chirp` complex samples come first, then frame 1, and so on.
- `cap_NN.json` is the sidecar. It holds `n_frames`, `samples_per_chirp`, `frame_rate_hz`, `range_per_bin_m`, `scale_factor` and the format string.

For each capture:

1. Form the range profile of every chirp with an unwindowed complex FFT over fast time, of length `samples_per_chirp`. Range bin k lies at `k * range_per_bin_m` metres.
2. Remove static clutter by subtracting each bin's mean over slow time (frames).
3. The subject bin is the bin with the largest mean magnitude over frames, after clutter removal. Only bins whose range is within 0.3 to 1.5 m (inclusive) are eligible.
4. Take the unwrapped phase of the subject bin over slow time. The breathing rate is the dominant frequency of that phase in the 0.08 to 0.5 Hz band. Use a spectral estimate with a frequency resolution of 0.01 Hz or finer.

Write `/root/work/range_results.csv` with the header `capture_id,range_bin,range_m,breathing_rate_bpm` and one row per capture (`cap_01`, ...). The columns are:

- `range_bin`: an integer.
- `range_m`: the bin's range, rounded to 2 decimals.
- `breathing_rate_bpm`: breaths per minute, rounded to 1 decimal.
