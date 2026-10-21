**Inputs.** `/root/data/*.npz` holds 100 traces. Each file has `data` (12000×3 float), `dt` (seconds per sample) and `channels` (a string like `"DPE,DPN,DPZ"`). Other keys may exist, so inspect them cheaply:
```
ls /root/data | head -3; ls /root/data | wc -l
python -c "import numpy as np,glob;f=sorted(glob.glob('/root/data/*.npz'))[0];d=np.load(f,allow_pickle=True);print({k:(d[k].shape,d[k].dtype) for k in d.files});print(d['dt'],d['channels'])"
```
- Print the scalar/string fields of 2–3 files, but never print the whole `data` array.
- Check whether any field looks like a label (e.g. p/s index or arrival). If one exists, use it only to tune thresholds or choose a model locally, never as the output.
- `channels` may be a 0-d array, so use `str(d['channels'])`.
- `dt` may differ between files, e.g. 0.01 s (100 Hz). Compute it per file.

**Method choice (from the skills).**
- Deep-learning pickers give high sensitivity with fewer false positives than STA/LTA. STA/LTA picks are imprecise and noisy, so they will hardly reach F1 ≥ 0.7/0.6 at a 0.1 s tolerance.
- Use SeisBench pretrained models: `PhaseNet` is the primary choice, and `EQTransformer` is an alternative.
- SeisBench works on ObsPy Streams of arbitrary length, so do not segment the data yourself.
- Do not assume exactly one P and one S per trace. Multiple picks or none are allowed.

**Building the Stream.** Make one `Trace` per channel. Give all three the same network, station and location. The channel code's last letter must be the component (Z/N/E; SeisBench maps components by that letter).
```python
import numpy as np, obspy, glob, os
from obspy import Trace, Stream, UTCDateTime
t0 = UTCDateTime(2000,1,1)
def load(f):
    d = np.load(f, allow_pickle=True)
    x = np.asarray(d['data'], dtype=np.float64)      # (12000,3)
    if x.shape[0] == 3 and x.shape[1] != 3: x = x.T
    dt = float(d['dt']); chans = str(d['channels']).split(',')
    st = Stream()
    for i, ch in enumerate(chans):
        y = x[:, i] - x[:, i].mean()
        s = y.std()
        y = y / s if s > 0 else y                    # own normalization
        st += Trace(data=y.astype(np.float32), header=dict(
            network='XX', station='STA', location='', channel=ch.strip(),
            sampling_rate=1.0/dt, starttime=t0))
    return st, dt
```
Pitfalls from the skills:
- With tiny amplitudes (≤1e-10), SeisBench's internal `(x-mean)/(std+eps)` destroys the signal. Normalize yourself as above, or multiply by 1e10 first.
- Guard against NaN or all-zero channels by replacing them with zeros (std = 0, so skip the division).
- If channels end in 1/2 instead of N/E, rename them to `..N`/`..E`, for example `ch[:-1]+'N'`.

**Running the model.**
```python
import seisbench.models as sbm
print(sbm.PhaseNet.list_pretrained())     # e.g. original, stead, instance, ethz, scedc, geofon...
model = sbm.PhaseNet.from_pretrained("instance")   # try a few
model.eval()
out = model.classify(st, P_threshold=0.3, S_threshold=0.3)   # kwargs accepted by PhaseNet
for p in out.picks:
    idx = int(round((p.peak_time - t0) * (1.0/dt)))
    phase = p.phase                                  # 'P' or 'S'
```
- `annotate(st)` returns probability traces, e.g. channels ending `_P`, `_S`, `_N`. You can apply your own peak picking with `scipy.signal.find_peaks(prob, height=thr, distance=int(1/dt))` if needed.
- The model resamples internally, but `model.sampling_rate` is 100 Hz. Manual resampling is optional.
- Weights download on first use and are cached afterward. If there is no network, check `~/.seisbench` for cached weights.
- If no model weights are available, fall back to `obspy.signal.trigger.recursive_sta_lta` plus `trigger_onset`. This is a weak fallback.
- The batch size can be raised and the CPU is fine for 100 traces.

**Improving F1.**
- If label fields exist, compute per-phase F1 locally and tune the model, version and thresholds (0.1–0.5) to maximize it. A pick is a true positive if it lies within `round(0.1/dt)` samples of a label, matching each label at most once. FP = unmatched picks, FN = unmatched labels, and F1 = 2TP/(2TP+FP+FN).
- Lower thresholds raise recall but add false positives.
- Without labels, use moderate thresholds (P ≈ 0.3, S ≈ 0.3) and the "instance" or "stead" weights. Only consider "original" if the data look like it fits.
- Optionally ensemble models by averaging `annotate` probabilities before peak picking.

**Plan.**
1. Inspect the inputs with the one-liners above: keys, `dt`, channels, shape and amplitude scale (`np.abs(x).max()`).
2. Check that seisbench imports, then list the pretrained weights.
3. Write `/root/pick.py`, which loops over all files, builds Streams, classifies, converts picks to indices and writes the CSV.
4. Run it, printing only counts per phase and the number of files with no picks.
5. Validate the output with `head /root/results.csv` and pandas (columns, phase values, integer indices within [0, 12000)).
6. If labels exist, evaluate F1 per phase and re-tune.

**Output.** Write `/root/results.csv` with header `file_name,phase,pick_idx`.
- One row per pick.
- `file_name` is the npz file name, the basename like `xxx.npz` as it appears in `/root/data`.
- `phase` is exactly `P` or `S`.
- `pick_idx` is an integer sample index into the 12000-sample trace.
- Files with no picks can be omitted. Several picks per phase per file are allowed.
```python
import pandas as pd
pd.DataFrame(rows, columns=['file_name','phase','pick_idx']).to_csv('/root/results.csv', index=False)
```
