**Inputs and tools**
- Waveforms: `obspy.read("/root/data/wave.mseed")` gives a Stream. Inspect it cheaply:
  - `print(st.__str__(extended=False))` or `len(st)`
  - the set of `(tr.stats.network, tr.stats.station, tr.stats.location, tr.stats.channel)`
  - the sampling rates, the start/end times, and `max(abs(tr.data).max() for tr in st)`
- Prepare the stream: `st.merge(fill_value=0)` to remove gaps/overlaps, then `st.detrend("demean")`.
- Small amplitudes: if values are tiny (≤1e-10, e.g. already converted to m/s), multiply the data by 1e10 before picking. SeisBench normalizes with `(x - mean)/(std + eps)`, and for tiny values the epsilon destroys the signal.
- You do not need to split the data into segments. SeisBench handles continuous data of any length, with many events per trace.
- Stations: `pd.read_csv("/root/data/stations.csv")`. Run `head -3` first. It has one row per channel, so collapse to one row per station with `drop_duplicates(["network","station"])`. The `response` column (sensitivity) is only needed if you use amplitudes, so skip it.

**Picking (SeisBench)**
```python
import seisbench.models as sbm
model = sbm.PhaseNet.from_pretrained("original")   # alternatives: "instance","stead","ethz"; or sbm.EQTransformer.from_pretrained("original")
out = model.classify(st, batch_size=256, P_threshold=0.3, S_threshold=0.3)
picks = out.picks if hasattr(out, "picks") else out   # newer versions return ClassifyOutput
```
- Each pick has these attributes: `trace_id` (formatted "NET.STA.LOC", with no channel), `peak_time` (UTCDateTime), `peak_value` (probability) and `phase` ("P"/"S").
- Weights download on first use and are cached in `~/.seisbench`. If one weight name fails, try another listed by `sbm.PhaseNet.list_pretrained()`.
- The model resamples automatically, to `model.sampling_rate` (100 Hz for PhaseNet).
- Print the pick counts by phase as a sanity check.

Build the picks DataFrame:
```python
rows=[dict(id=".".join(p.trace_id.split(".")[:2]), timestamp=pd.Timestamp(p.peak_time.datetime),
           type=p.phase.lower(), prob=float(p.peak_value), amp=0.0) for p in picks]
pick_df=pd.DataFrame(rows)
```
Use the same `"NET.STA"` id convention in the stations DataFrame. The ids must match exactly.

**Station coordinates (projected km)**
```python
from pyproj import Proj
lon0,lat0=sta.longitude.mean(),sta.latitude.mean()
proj=Proj(f"+proj=sterea +lon_0={lon0} +lat_0={lat0} +units=km")
x,y=proj(sta.longitude.values, sta.latitude.values)
stations=pd.DataFrame({"id":sta.network+"."+sta.station,"x(km)":x,"y(km)":y,"z(km)":-sta.elevation_m/1000})
```
Elevation becomes negative z, because z is depth.

**Association (GaMMA)**
```python
from gamma.utils import association, estimate_eps
vp=6.0; vs=vp/1.75
xmin,xmax=stations["x(km)"].min(),stations["x(km)"].max(); ymin,ymax=...
config={"dims":["x(km)","y(km)","z(km)"],"vel":{"p":vp,"s":vs},"use_amplitude":False,
 "method":"BGMM","oversample_factor":5.0,
 "x(km)":(xmin-50,xmax+50),"y(km)":(ymin-50,ymax+50),"z(km)":(0,30),
 "bfgs_bounds":((xmin-51,xmax+51),(ymin-51,ymax+51),(0,31),(None,None)),
 "use_dbscan":True,"dbscan_eps":estimate_eps(stations,vp),  # or 10–15 s
 "dbscan_min_samples":3,"dbscan_min_cluster_size":500,"dbscan_max_time_space_ratio":10,
 "min_picks_per_eq":5,"min_p_picks_per_eq":0,"min_s_picks_per_eq":0,"max_sigma11":2.0,"ncpu":4}
events,assign=association(pick_df,stations,config,method=config["method"])
```
- `association` returns `(events, assignments)`. `events` is a list of dicts with `time` (ISO string), `num_picks`, `x(km)` and so on.
- The amp column is ignored when `use_amplitude=False`. Keep it anyway to be safe.
- The `vel` key defaults to `{"p":6,"s":3.47}`. Set it explicitly to vp/1.75 as above.
- `min_stations` defaults to 5. If the network is small, lower `min_picks_per_eq` and `min_stations` (to about 3–4) to fit the number of stations.

**Tuning and pitfalls**
- F1 penalizes both missed and spurious events. Two failure modes to watch:
  - Too many events: from low thresholds, low `min_picks`, or BGMM splitting one event into several.
  - Too few events: from high thresholds or a too-strict `max_sigma11`.
- Deduplicate after association. Sort events by time and merge any events less than ~3 s apart, keeping the one with the most picks. Duplicates within 5 s become false positives.
- Sanity checks:
  - Compare the event count with picks/stations. Roughly, each event should have about one P and one S per station.
  - Check that the times fall inside the waveform time span.
  - Check that `num_picks` values are reasonable.
- If BGMM is slow, try `method="GMM"` with `oversample_factor=1.0`.
- Install packages only if they are missing: `pip install seisbench`, `pip install git+https://github.com/wayneweiqiang/GaMMA.git`, `pyproj`. Check first with `python -c "import seisbench,gamma,pyproj"`.

**Output**
- Write `/root/results.csv`, one row per event, with a required column `time` in ISO format without a timezone, e.g. `2019-07-04T22:00:01.234`.
- Convert with `pd.to_datetime(ev["time"]).strftime("%Y-%m-%dT%H:%M:%S.%f")`, stripping any "Z" or "+00:00".
- Extra columns are allowed: x, y, z, num_picks and so on.

**Step plan (keep output short)**
1. Check imports. Run `head -3 stations.csv`, `wc -l`, and a one-liner summarizing the stream: trace count, stations, rate, time span, max amplitude.
2. Write `/root/run.py` covering: load → merge/scale → classify → save the picks to `/root/picks.csv` → project the stations → GaMMA → dedupe → write the results.
3. Run it and print only the counts: picks P/S, events before and after dedupe, and the first 5 times.
4. Verify the CSV with `head /root/results.csv`: the column is `time`, there is no timezone, and the times are within the data span.
5. If the counts look off, adjust the thresholds, `min_picks_per_eq` and `dbscan_eps`. Reuse the saved picks so you do not re-run the picker.
