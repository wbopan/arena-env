# Locate sprites in two Mario frames

Two RGB screenshots are provided at `/root/work/frames/frame_001.png` and `/root/work/frames/frame_002.png`. Each is 64 by 40 pixels. The three 5-by-5 reference sprites are `/root/work/coin.png`, `/root/work/enemy.png`, and `/root/work/turtle.png`. Rather than reporting only totals, produce the location and identity of every visible reference sprite.

Convert screenshots and references to 8-bit grayscale using Pillow's `L` mode before comparing them. A detection is a 5-by-5 region whose grayscale pixels exactly equal a complete reference sprite, with no rotation or reflection. Coordinates are zero-based pixel coordinates of the region's upper-left corner, measured from the screenshot's upper-left corner. All detections lie wholly within their frame. Treat each matching region as one detection; do not infer objects from similar colors elsewhere.

Write exactly one UTF-8 CSV file at `/root/work/sprite_locations.csv`. Its header must be `frame,x,y,kind`, in that order. In `frame`, use the input filename only, such as `frame_001.png`; `x` and `y` must be decimal integers, and `kind` must be exactly `coin`, `enemy`, or `turtle`. Sort rows first by frame filename, then by numeric `y`, then by numeric `x`. Include no totals or extra columns, and leave the inputs unchanged.
