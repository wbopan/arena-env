# Detect keyframes in a GIF and count coins

`/root/work/level.gif` is an animated GIF screen capture of a Super Mario run. Find its keyframes and count the coins visible in each keyframe.

## Conventions

- **Frames.** Frames are indexed from 0 in file order. Decode each frame as it is displayed: the fully composited RGB image.
- **Durations.** Each frame's display duration is stored in the GIF, in milliseconds.
- **Grayscale.** For each frame, compute float luma `Y = 0.299*R + 0.587*G + 0.114*B` per pixel. Do not round.
- **Keyframes.**
  - Frame 0 is always a keyframe.
  - For each later frame i, compute the mean absolute luma difference between frame i and the most recent keyframe.
  - Frame i is a new keyframe if that difference is strictly greater than 30.
- **Timestamp.** The timestamp of frame i is the sum of the durations of frames 0 to i-1. So frame 0 has timestamp 0.
- **Coins.** Coins are drawn in the exact RGB color (252, 188, 60).
  - The number of coins in a frame is the number of 8-connected regions of pixels with exactly that color.
  - Similar-looking colors are not coins.

## Output

Write `/root/work/keyframes.json` as a JSON object with this structure:

```json
{"n_frames": <total number of frames>, "keyframes": [{"index": <int>, "timestamp_ms": <int>, "coins": <int>}, ...]}
```

List the keyframes in ascending `index` order. All values are integers.
