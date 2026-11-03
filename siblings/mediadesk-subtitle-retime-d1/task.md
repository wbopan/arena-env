# Re-time a subtitle file

`/root/work/input.srt` is an SRT subtitle file and `/root/work/job.json` holds `offset_ms`, a shift in milliseconds (it can be negative).

Write `/root/work/output.srt`: every timestamp moved by `offset_ms`. A cue whose new end is at or before 00:00:00,000 is removed; a cue whose new start is negative starts at 00:00:00,000. Keep each cue's text lines unchanged and in order. Number the remaining cues 1, 2, 3, ... in order. Use the format `HH:MM:SS,mmm --> HH:MM:SS,mmm` and separate cues with one blank line.
