# AIC phase picks and S-P distance

`/root/work` contains three-component station records named `sta_*.npz`. Each file has these fields:
- `data`: float array of shape (n_samples, 3)
- `dt`: sampling interval in seconds. It differs between stations.
- `channels`: comma-separated names in column order. The order varies, and each name ends in Z, N or E.
- `station`: the station code

## AIC picker

Pick phases with the Maeda AIC picker. For a segment y of length M (0-based), compute, for every k with 10 <= k <= M-11:

AIC(k) = k*ln(var(y[0:k])) + (M-k-1)*ln(var(y[k:M]))

Here var is the population variance (divide by the count), and y[a:b] excludes index b. The pick is the k with the minimum AIC. On ties, take the smallest k.

## Picks and distance

- P pick: apply AIC to the entire vertical (Z) channel. Then p_idx = k.
- S pick: let w = p_idx + round(0.2/dt). Apply AIC to the north (N) channel samples from w to the end. Then s_idx = w + k, which is the index in the full trace.
- sp_time_s = (s_idx - p_idx)*dt.
- Hypocentral distance, with Vp = 6.0 km/s and Vs = 3.5 km/s: distance_km = sp_time_s*Vp*Vs/(Vp - Vs).

## Output

Write `/root/work/picks.json`:
```
{"stations": {"<code>": {"p_idx": int, "s_idx": int, "sp_time_s": float, "distance_km": float}, ...},
 "nearest_station": "<code with the smallest distance_km>"}
```
Include every station, keyed by its `station` code. Indices are 0-based integers. Round sp_time_s to 3 decimals and distance_km to 2 decimals.
