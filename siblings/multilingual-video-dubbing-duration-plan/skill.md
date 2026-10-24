## Reference notes

No audio processing is needed: the CSV already supplies raw TTS durations. Use Python standard-library `csv`, `json`, and `pathlib`; `ffmpeg`/`ffprobe` would not add information for this plan.

- Inspect only the first few lines of each input to confirm its layout. Parse SRT cues by **cue index**, not by their position in the file. Use timestamps from `segments.srt` only; ignore those in `target_text.srt`.
- SRT cues have an index line, a `start --> end` line, then one or more text lines; blank lines separate cues. Reading with `encoding="utf-8-sig"` tolerates a UTF-8 BOM. Join cue text lines with `" ".join(lines).strip()`.
- For `HH:MM:SS,mmm`, convert to seconds as `3600*h + 60*m + s + ms/1000`. Keep the unrounded result through all calculations. Ensure each speech window has positive duration.
- Read the CSV with `csv.DictReader`, converting `segment_index` to `int` and `tts_duration_sec` to `float`; map rows by index because their order is arbitrary. Read the language code with `.read_text(...).strip()`.

The task’s duration rules are the authority: `r = tts_duration / (end - start)`. A shorter clip leaves silence; a moderately longer clip is sped up to fit; above the specified threshold, speed up by 1.25 and trim the remaining excess. Calculate each trim and its summary total **before** rounding. Round numeric second fields and `tempo_factor` to three decimals only when constructing the JSON output; sort segments by unrounded `window_start_sec`.

Useful I/O pattern:

```python
from pathlib import Path
import csv, json

base = Path("/root/work")
with (base / "tts_durations.csv").open(newline="", encoding="utf-8-sig") as f:
    durations = {
        int(row["segment_index"]): float(row["tts_duration_sec"])
        for row in csv.DictReader(f)
    }

# After parsing cues and constructing the requested object:
(base / "dub_plan.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
```

Check that the two SRT index sets and the CSV index set match before writing, then reopen the JSON to inspect its segment count, ordering, and summary counts.
