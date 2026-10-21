# STA/LTA trigger on vertical channels

The directory `/root/work` contains several three-component seismic trace files named `trace_*.npz`. Each file has these fields:
- `data`: float array of shape (n_samples, 3)
- `dt`: sampling interval in seconds. It differs between files.
- `channels`: comma-separated channel names in column order. The order differs between files. The vertical channel is the one whose name ends in `Z`.

For each file, run a classic energy STA/LTA trigger on the vertical channel only:
1. Remove the mean of the whole vertical trace (x). Let e[i] = x[i]^2.
2. Set ns = round(0.5 / dt) and nl = round(5.0 / dt) samples.
3. For every 0-based index i >= nl - 1, compute:
   - STA(i) = mean of e[i-ns+1 ... i]
   - LTA(i) = mean of e[i-nl+1 ... i]
   Both windows are trailing and include sample i.
4. The trigger index is the first i where STA(i)/LTA(i) >= 3.0. If no index qualifies, the file has no trigger.

Write `/root/work/triggers.csv` with the header `file_name,trigger_idx,trigger_time_s`. Write exactly one row per input file, sorted by file name. The columns are:
- `file_name`: the base name, e.g. `trace_00.npz`
- `trigger_idx`: the 0-based sample index, as an integer
- `trigger_time_s`: trigger_idx * dt, rounded to 3 decimals

If a file has no trigger, write -1 in both numeric columns.
