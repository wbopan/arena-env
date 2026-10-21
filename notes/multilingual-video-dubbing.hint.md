1. Cat the 4 small text files, ffprobe input.mp4, and check which TTS engines exist (prefer kokoro/edge-tts over espeak); use the reference_target_text as the TTS text.
2. In one Python script: TTS → `ffmpeg -ac 1 -ar 48000` → atempo to the window length → pad or trim to exact samples → 50 ms fades → two-pass loudnorm to −23 LUFS (add `-ar 48000`) → /outputs/tts_segments/seg_0.wav.
3. Place the segment sample-exactly in a numpy silence track of the original duration, then mux with `-map 0:v -c:v copy -c:a aac -ar 48000 -ac 1` → /outputs/dubbed.mp4.
4. Write /outputs/report.json with language codes, measured LUFS (from ebur128), drift, and duration_control.
5. Verify with ebur128 and ffprobe that drift ≤ 0.2 s and the start error < 10 ms.
