**Inputs to inspect cheaply (one or two commands)**
- Print the small text files: `cat /root/target_language.txt; head -40 /root/segments.srt /root/source_text.srt /root/reference_target_text.srt`. There is likely only one segment, because only `seg_0.wav` is required. Do not assume that; loop over all windows.
- Get video facts: `ffprobe -v error -show_entries format=duration:stream=index,codec_type,codec_name,sample_rate,channels -of json /root/input.mp4`.
- Check which TTS engines exist:
  `python3 -c "import importlib.util as u;print([m for m in ['kokoro','edge_tts','gtts','TTS','pyttsx3','soundfile','pyloudnorm','numpy'] if u.find_spec(m)])"; which espeak-ng espeak piper ffmpeg`.
- Engine preference for "human level" quality:
  1. Neural offline (Kokoro, Piper, Coqui TTS).
  2. Cloud (edge-tts or gTTS). These need network, so test with one short call.
  3. espeak-ng only as a last resort. It is formant-based and judged non-natural.
- Kokoro for Japanese: `KPipeline(lang_code='j')`, voice e.g. `jf_alpha`, output 24 kHz. Other lang codes: 'a' en-US, 'z' zh, 'e' es, 'f' fr, 'h' hi, 'i' it, 'p' pt.
- edge-tts example: `edge-tts --voice ja-JP-NanamiNeural --text "..." --write-media t.mp3`. Other voices: zh-CN-XiaoxiaoNeural, es-ES-ElviraNeural, fr-FR-DeniseNeural, de-DE-KatjaNeural.
- Always check the TTS native sample rate with ffprobe before resampling.

**SRT parsing**
- Blocks are: index, `HH:MM:SS,mmm --> HH:MM:SS,mmm`, then text lines.
- Seconds = h*3600 + m*60 + s + ms/1000.
- Window times come from segments.srt. source_text comes from source_text.srt.
- target_text must be the reference_target_text.srt text. Use it verbatim as the TTS input.
- Language codes are ISO codes ("en", "ja", ...). Take the target code from target_language.txt; map a name like "Japanese" to "ja". The source is presumably "en".

**Per-segment processing (sample rate 48000, mono)**
1. Synthesize to a raw file, then convert: `ffmpeg -y -i raw -ac 1 -ar 48000 tmp.wav`.
2. Trim leading and trailing TTS silence so the duration reflects actual speech. Use `silenceremove`, or numpy thresholding.
3. Fit the clip to the window, where W = window_end − window_start and T = TTS duration.
   - Compute ratio r = T/W. If r ≠ 1 beyond ~2%, apply `atempo=r`. Chain atempo stages if r is outside 0.5–2.0. Set duration_control = "rate_adjust".
   - If the clip is slightly shorter, pad zeros at the end ("pad_silence").
   - If it is still longer, cut it ("trim").
   - Finally force the exact length: `round(W*48000)` samples via numpy.
4. Clean up, per the TTS skill: `highpass=f=20,lowpass=f=16000`, plus 50 ms fades at both ends (`afade=t=in:d=0.05`, and `afade=t=out:st=W-0.05:d=0.05`). Apply fades after padding or trimming.
5. Normalize last to −23 LUFS, true peak −1.5 dBTP.
   - Pitfall: `loudnorm` resamples internally to 192 kHz, so always add `-ar 48000 -ac 1`.
   - Single-pass loudnorm on short clips is imprecise. Do two-pass: first run `loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json` with `-f null -`, then run `loudnorm=I=-23:TP=-1.5:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true`.
   - Alternative if pyloudnorm exists: `gain = -23 - meter.integrated_loudness(x)`; then `x *= 10**(gain/20)`, and check the peak stays below ~0.84.
   - If you change tempo or length after normalizing, re-normalize.
6. Save to `/outputs/tts_segments/seg_0.wav` (seg_i for others) as PCM s16 or float, 48 kHz mono. Run `mkdir -p /outputs/tts_segments` first.
7. Verify loudness: `ffmpeg -i seg_0.wav -af ebur128=peak=true -f null - 2>&1 | grep -A3 Summary`. The "I:" value should be −23 ±0.5. Report this as measured_lufs.

**Building the dubbed track**
- Length is the original duration D, taken from ffprobe format duration.
- Use numpy: `track = zeros(round(D*48000))`, then `track[round(ws*48000): +len(seg)] = seg`. This gives sample-exact placement, unlike adelay rounding.
- The track should contain only the dub, not the original speech.
- placed_start = ws and placed_end = ws + len(seg)/48000. tts_duration_sec = len(seg)/48000.
- drift_sec = placed_end − window_end. It must be within ±0.2 s, and the start must be within 10 ms.

**Muxing**
```
ffmpeg -y -i /root/input.mp4 -i track.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 1 -shortest /outputs/dubbed.mp4
```
- Drop `-shortest` if it cuts the video. The track already equals D.
- Verify the result with `ffprobe` on the a:0 stream (sample_rate=48000, channels=1) and on format duration. That duration is new_duration_sec and should be ≈ original_duration_sec.

**report.json (/outputs/report.json)**
Use exactly these keys:
- source_language, target_language (codes)
- audio_sample_rate_hz: 48000
- audio_channels: 1
- original_duration_sec, new_duration_sec
- measured_lufs
- speech_segments: a list, each entry with window_start_sec, window_end_sec, placed_start_sec, placed_end_sec, source_text, target_text, window_duration_sec, tts_duration_sec, drift_sec, duration_control ("rate_adjust" | "pad_silence" | "trim").

Write it with `json.dump(..., ensure_ascii=False, indent=2)` and round floats to about 3 decimals.

**Plan (≈10 commands)**
1. Inspect the inputs and available tools, as above.
2. Smoke-test the best TTS engine on one short phrase.
3. Write a single `/root/dub.py` that does: parse SRTs → TTS → 48 kHz mono → silence-trim → atempo fit → exact length → filters/fades → two-pass loudness → write seg wav → build the full track → mux → ebur128 measure → report.json.
4. Run it, then check: ebur128 on seg_0.wav, ffprobe on dubbed.mp4 (48 kHz, 1 channel, video stream present, duration), `cat report.json`, and that |drift| ≤ 0.2 s and the placed start equals the window start.
5. Fix anything that is off and re-run.
