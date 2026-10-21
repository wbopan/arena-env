# Assemble a dubbed dialogue track

These inputs are in /root/work:

- `segments.srt`: the speech windows (SRT, `HH:MM:SS,mmm`). Cue index k corresponds to the clip `tts/seg_k.wav`.
- `tts/seg_k.wav`: the synthesized dubbing clips. Each is mono, 16-bit PCM, 16000 Hz.
- `timeline.json`: `{"sample_rate": 16000, "duration_sec": D}`.

Build the dubbed track as follows. Work in int16 sample units, where full scale is 32768.

1. **Loudness match.** For each clip, compute the RMS over all of its samples: `rms = sqrt(mean((x/32768)^2))`. Multiply the whole clip by `10^(-20/20) / rms`, so its RMS becomes -20 dBFS. Measure on the whole, untrimmed clip.
2. **Window bounds.** The window start sample is `s = round(start_sec * 16000)` and the end sample is `e = round(end_sec * 16000)`. The window length is `n = e - s`.
3. **Trim or pad.** If the clip has more than n samples, keep only its first n samples (trim). Otherwise, place it as-is and leave the rest of the window silent (pad).
4. **Placement.** Start from a silent timeline of `round(D * 16000)` samples. Put the clip's first sample at index s. Windows do not overlap.
5. **Quantize.** Round to the nearest integer and clip to [-32768, 32767].

Write `/root/work/dubbed_track.wav`:

- mono, 16-bit PCM, 16000 Hz;
- exactly `round(D * 16000)` frames;
- digital silence (value 0) everywhere outside the placed clips.

Sample values must match the procedure above within 1 LSB.
