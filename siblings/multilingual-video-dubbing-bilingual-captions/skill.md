## Reference notes

Use Python’s standard library; no audio or video tool is needed. Treat the files as UTF-8 text. SRT timestamps use a comma before milliseconds (`HH:MM:SS,mmm`); WebVTT uses a period (`HH:MM:SS.mmm`). Do timing arithmetic in **integer milliseconds**.

- Parse each SRT cue into `(integer_index, start_ms, end_ms, text)`. Normalize line endings, separate cues at blank lines, and join a cue’s text lines with `" ".join(lines)`. Key all three files by **integer index**, regardless of file order or the text files’ timestamps.
- Sort the window records by **original start time** before applying neighbor constraints. For a window `(start, end)` at position `i`:
  ```python
  new_start = max(0, start - 80)
  if i > 0:
      new_start = max(new_start, windows[i - 1].end)    # original end

  new_end = end + 80
  if i + 1 < len(windows):
      new_end = min(new_end, windows[i + 1].start)       # original start
  ```
  Do not use a neighbor’s extended time for either clamp.
- `html.escape(text, quote=False)` escapes `&`, `<`, and `>` without changing quotes. Apply it to **caption text only**, after joining lines; leave `EN: ` and the uppercase language-code label unescaped.
- Format milliseconds with `divmod` into hours, minutes, seconds, and a three-digit millisecond field. Write UTF-8 with `WEBVTT\n\n` first, then each cue as an identifier line, timing line (` --> `), two caption lines, and a blank line. Use `Path(...).read_text(encoding="utf-8")` and `write_text(..., encoding="utf-8")` if convenient.
