**Goal.** Write two files to the current workspace (cwd, not data/):
- `compressed_video.mp4`: the input with the opening and the long pauses cut out.
- `compression_report.json`: must contain these keys:
  - `original_duration_seconds`, `compressed_duration_seconds`, `removed_duration_seconds`, `compression_percentage` (all numbers);
  - `segments_removed`: a list of `{"start","end","duration"}` numbers in seconds.

The checks are:
- original ≈ compressed + removed;
- compression_percentage = removed / original × 100;
- each segment satisfies 0 ≤ start < end ≤ original and duration = end − start;
- the compression rate falls in a plausible range.

A reference run in the skills removed about 41% (a ~221 s opening plus ~28 s of pauses on a ~600 s video). Treat that as an example of scale, not a target.

**Tools.** The skills ship scripts under `/root/.claude/skills/<name>/scripts/`. Check they exist with `ls /root/.claude/skills/*/scripts`. The pipeline, in order:

1. Extract audio (mono 16 kHz WAV):
   `python3 /root/.claude/skills/audio-extractor/scripts/extract_audio.py --video data/input_video.mp4 --output audio.wav`
2. Compute per-second RMS energy, `sqrt(mean(samples^2))`. Output: energies.json with `energies` list and `stats`.
   `python3 /root/.claude/skills/energy-calculator/scripts/calc_energy.py --audio audio.wav --output energies.json`
3. Detect the opening (initial silence). It takes a baseline from the first 60 s, smooths with a 30 s moving average, and finds where the smoothed energy exceeds baseline × 1.5. The output is a `segments` list such as `[{"start":0,"end":N,...}]`.
   `python3 /root/.claude/skills/silence-detector/scripts/detect_silence.py --energies energies.json --output opening.json`
   - Tuning: `--threshold-multiplier` (lower = more sensitive), `--initial-window`, `--smoothing-window`.
   - If the result is empty, the opening is noisy (static frames with noise), so its energy is not near zero. Inspect the energy curve and pick the transition by hand.
4. Detect pauses after the opening, using a local dynamic threshold. A second counts as low when energy < local_avg(30 s window) × 0.5. Runs of low seconds of at least 2 s become pauses.
   `python3 /root/.claude/skills/pause-detector/scripts/detect_pauses.py --energies energies.json --start-time <opening_end> --output pauses.json`
   - Defaults are `--threshold-ratio 0.5 --min-duration 2 --window-size 30`. Keep them; they match "pauses > 2 s" and "keep teaching content".
5. Combine the two segment lists (output is sorted, with a `segments` key):
   `python3 /root/.claude/skills/segment-combiner/scripts/combine_segments.py --segments opening.json pauses.json --output all_segments.json`
6. Cut the video. This uses ffmpeg filter_complex trim/atrim + concat and re-encodes with libx264/aac:
   `python3 /root/.claude/skills/video-processor/scripts/process_video.py --input data/input_video.mp4 --output compressed_video.mp4 --remove-segments all_segments.json`
   - Run it in the background with a log, or with a long timeout. Encoding takes roughly 0.3× the video duration, so a few minutes here.
7. Write the report. It uses ffprobe durations, and its segments may include a `type` field (extra keys are fine).
   `python3 /root/.claude/skills/report-generator/scripts/generate_report.py --original data/input_video.mp4 --compressed compressed_video.mp4 --segments all_segments.json --output compression_report.json`

**Manual fallback** (if the scripts are missing or fail):
- Audio: `ffmpeg -y -i data/input_video.mp4 -vn -ac 1 -ar 16000 -acodec pcm_s16le audio.wav`.
- Energy in numpy:
  ```python
  x = np.frombuffer(open('audio.wav','rb').read()[44:], np.int16).astype(float)
  e = [np.sqrt(np.mean(x[i*16000:(i+1)*16000]**2)) for i in range(len(x)//16000)]
  ```
- Opening and pauses: apply the same rules as above.
- Video cut: build the filter from the keep intervals (the complement of the removed segments):
  ```
  [0:v]trim=start=S:end=E,setpts=PTS-STARTPTS[vi];
  [0:a]atrim=start=S:end=E,asetpts=PTS-STARTPTS[ai]; ...
  [v0][a0][v1][a1]...concat=n=K:v=1:a=1[outv][outa]
  ```
  Run it with:
  `ffmpeg -y -i in -filter_complex_script f.txt -map [outv] -map [outa] -c:v libx264 -preset veryfast -crf 23 -c:a aac compressed_video.mp4`
- Durations: `ffprobe -v error -show_entries format=duration -of csv=p=0 file`.

**Plan within the budget:**
1. `ffprobe` the input duration. Run `ls` on the skills directory.
2. Extract audio and compute energies.
3. Print a compact energy view instead of the whole file:
   `python3 -c "import json;e=json.load(open('energies.json'))['energies'];print(len(e));print([round(v) for v in e[::5]])"`
   Look for the opening transition, which is a step up in energy.
4. Run the opening detection and check its `end` against the curve.
5. Run pause detection from the opening end. Print the number of segments and the total.
6. Sanity-check the result:
   - Removed time should be the opening plus a modest pause total.
   - Do not remove large teaching chunks. If the pause total looks huge, raise `--min-duration` or lower `--threshold-ratio`.
7. Combine the segments, process the video, and generate the report.

**Verify at the end:**
- Run ffprobe on `compressed_video.mp4`; it must have both a video and an audio stream.
- Load `compression_report.json` and check all keys are present.
- Check `abs(original - (compressed + removed))` is small (< 1–2 s).
  - If the encoder's frame rounding makes it drift, recompute `removed_duration_seconds` as the sum of the segment durations. Then set `compressed_duration_seconds` to the ffprobe value and confirm consistency, or set compressed = original − removed.
- Check the percentage equals removed/original×100.
- Check segments are sorted and non-overlapping, with duration = end − start.
