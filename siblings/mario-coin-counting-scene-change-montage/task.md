# Build a grayscale scene-change montage

Eight consecutive RGB frames from a short Mario capture are stored at `/root/work/frames/frame_000.png` through `/root/work/frames/frame_007.png`. Every frame is 32 pixels wide and 24 pixels high. Small sprite movements can occur without a scene change; a large overall change marks a new scene.

Select frame 000 unconditionally. For each later frame, compare it with the immediately preceding input frame, not with the most recently selected frame. Convert both frames to 8-bit grayscale using Pillow's `L` mode, then compute the arithmetic mean of the absolute differences across all 768 corresponding pixels. Select the later frame if and only if that mean is at least 25.0 grayscale levels. Perform the comparison using the original input frames, including frames that were not selected.

Create exactly one output file, `/root/work/scene_montage.png`. It must be an 8-bit grayscale PNG whose height is 24 pixels and whose width is 32 pixels times the number of selected frames. Place the complete grayscale selected frames side by side, left to right in chronological order, without gaps, borders, scaling, captions, or other modifications. Do not alter the input files. Pixel values in the montage must equal the selected frames' Pillow `L` values exactly.
