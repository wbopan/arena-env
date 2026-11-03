# Edit list runtime

`/root/work/edl.csv` lists the clips of an edit with source timecodes `src_in` and `src_out` (SMPTE `HH:MM:SS:FF`) and a `status`. `/root/work/job.json` gives the frame rate `fps` (non-drop). `src_out` is exclusive: 00:00:01:00 to 00:00:02:00 at 30 fps is 30 frames. Clips whose status is `skip` are not in the cut.

Write `/root/work/runtime.json` as `{"clips": [{"clip_id": ..., "frames": ...}, ...], "total_frames": N, "total_timecode": "HH:MM:SS:FF"}`: the clips in the cut, in file order, with their lengths in frames (integers), the sum, and the sum as a timecode at the same rate counted from 00:00:00:00.
