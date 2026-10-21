# Camera motion labels from tracked points

A feature tracker produced point correspondences between consecutive sampled frames of a video.

Inputs:
- `/root/work/meta.json`: `{"num_frames": N}`.
- `/root/work/tracks.csv`: columns `pair,x0,y0,x1,y1`. Each row is one tracked point. It appears at `(x0,y0)` in sampled frame `pair` and at `(x1,y1)` in frame `pair+1`. Coordinates are in pixels, with the origin at the image centre, x pointing right and y pointing down.

For each pair, fit the similarity model `x1 = a*x0 - b*y0 + tx`, `y1 = b*x0 + a*y0 + ty` by ordinary least squares. Use all points of the pair and no outlier rejection. Let `s = sqrt(a^2 + b^2)` and `rot = atan2(b, a)`. The labels of the pair are:
- if `|s-1| > 0.02`: "Dolly In" when s > 1, otherwise "Dolly Out"
- if `|rot| > 0.01`: "Roll Right" when rot > 0, otherwise "Roll Left"
- if `|tx| > 2` and `|tx| >= |ty|`: "Pan Left" when tx > 0, otherwise "Pan Right"
- if `|ty| > 2` and `|ty| > |tx|`: "Tilt Up" when ty > 0, otherwise "Tilt Down"
- if none of these apply: ["Stay"]

Sampled frame i (0 <= i <= N-2) gets the labels of pair i. The last frame, N-1, repeats the labels of frame N-2.

Output: write `/root/work/pred_instructions.json`, a JSON object.
- Each key is a half-open interval `"start->end"` (integers) covering frames start..end-1.
- Each value is the list of labels for those frames.
- Merge consecutive frames with identical label sets into one maximal interval, so adjacent intervals have different label sets.
- The intervals must cover frames 0..N-1 exactly once, so the last key ends at N.
- The order of labels inside a list does not matter.
