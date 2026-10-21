# Dubbing duration-control plan

You are preparing a dub. These inputs are in /root/work:

- `segments.srt`: the authoritative speech windows (SRT, `HH:MM:SS,mmm`). Cue index k identifies segment k.
- `target_text.srt`: the translated lines. Match them to segments by cue index only. Their timestamps are approximate and must be ignored.
- `tts_durations.csv`: columns `segment_index,tts_duration_sec`. Each row gives the duration of the raw synthesized clip for one segment. Rows are in arbitrary order.
- `target_language.txt`: the target language code.

For each segment, compute `window_duration = end - start` and `r = tts_duration / window_duration`. Then choose the duration control:

- **r <= 1**: `pad_silence`. Set tempo_factor 1.0, trimmed_sec 0, and speech_end_sec = start + tts_duration.
- **1 < r <= 1.25**: `rate_adjust`. Set tempo_factor = r, trimmed_sec 0, and speech_end_sec = end.
- **r > 1.25**: `trim` (speed up by 1.25, then cut the tail). Set tempo_factor 1.25, trimmed_sec = tts_duration/1.25 - window_duration, and speech_end_sec = end.

Write `/root/work/dub_plan.json`:

```
{"target_language": "<code>",
 "segments": [{"index": int, "window_start_sec", "window_end_sec", "window_duration_sec", "tts_duration_sec", "duration_control", "tempo_factor", "trimmed_sec", "speech_end_sec", "target_text"}, ...],
 "summary": {"pad_silence": int, "rate_adjust": int, "trim": int, "total_trimmed_sec": float}}
```

Formatting rules:

- Sort segments by window_start_sec.
- Compute from unrounded values, then round all second values and tempo_factor to 3 decimals.
- `target_text` is the cue text, with multiple lines joined by a single space and stripped.
- `total_trimmed_sec` is the sum of the unrounded trimmed_sec values, rounded to 3 decimals.
