# Layout-shift scores from element rectangles

A rendering trace recorded, for each animation frame in which one element moved, the element's bounding rectangle before and after the shift. The file `/root/work/frames.json` has the shape `{"viewport": {"width": W, "height": H}, "frames": [{"id": str, "element": str, "previous": {"x","y","width","height"}, "current": {"x","y","width","height"}}, ...]}` (pixels; `x`,`y` are the top-left corner; the viewport spans `[0,W] x [0,H]`). Rectangles may lie partly or fully outside the viewport.

For every frame compute the layout-shift score as defined by the Layout Instability spec, specialised to one element:

- **impact_fraction**: clip `previous` and `current` to the viewport; take the area of the union of the two clipped rectangles, divided by `W*H`.
- **distance_fraction**: the move distance is the larger of `|current.x - previous.x|` and `|current.y - previous.y|` (unclipped); divide it by `max(W, H)` and cap at 1.0.
- **score** = impact_fraction * distance_fraction (computed from unrounded fractions).

Write `/root/work/shift_scores.csv` with header exactly:

`id,impact_fraction,distance_fraction,score`

One row per frame, sorted by `id` ascending (string order). All three numeric columns rounded to 6 decimals.
