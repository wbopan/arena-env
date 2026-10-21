1. Run ffprobe on data/input_video.mp4 and ls /root/.claude/skills/*/scripts. Then run audio-extractor and energy-calculator, and print a subsampled energy list to spot the noisy opening.
2. Run silence-detector to find the opening end (tune the multiplier or set it by hand if empty). Run pause-detector with --start-time at the opening end and the defaults (ratio 0.5, min 2 s, window 30).
3. Run segment-combiner, then video-processor to write ./compressed_video.mp4 (run in the background, a few minutes). Then run report-generator to write ./compression_report.json.
4. Verify that original ≈ compressed + removed, percentage = removed/original×100, and each segment has duration = end − start; fix the JSON if not.
