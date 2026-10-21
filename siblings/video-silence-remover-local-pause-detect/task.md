# Lecture Pause Detection (Local Dynamic Threshold)

The audio track of a short lecture clip has been extracted to `/root/work/lecture_audio.wav`. It is mono, 16-bit signed PCM, at a low sample rate; read the rate from the file header. Find the long pauses by comparing each second's energy with its local context.

Procedure:
1. Split the audio into consecutive 1-second windows. Each window is `sample_rate` samples long. Ignore any trailing partial window. Let N be the number of full windows. For window i, compute the RMS energy `sqrt(mean(x^2))` over its raw integer sample values.
2. The local average for second i is the mean energy of seconds max(0, i-7) through min(N-1, i+7) inclusive. This is a 15-second centered window that includes second i and is truncated at the edges.
3. Second i is "low" if its energy is strictly less than 0.5 x its local average.
4. Group consecutive low seconds into runs. Keep only runs that are at least 2 seconds long.

Write `/root/work/pauses.json` in this format:

```json
{
  "audio_duration_seconds": <N, integer>,
  "segments": [{"start": <int>, "end": <int>, "duration": <int>}],
  "total_segments": <int>,
  "total_duration_seconds": <int>
}
```

Field rules:
- `start` is the index of the first low second of a run.
- `end` is exclusive: the last low second + 1.
- `duration = end - start`.
- All times are whole seconds from the beginning of the file.
- Segments are sorted by `start`.
- `total_segments` is the number of kept segments.
- `total_duration_seconds` is the sum of their durations.
