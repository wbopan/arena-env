## Reference notes

Use Python’s standard-library `json` and `csv`; no browser or React tooling is needed for this recorded trace.

- Read with `json.load(open('/root/work/frames.json'))`. The viewport is `[0, W] × [0, H]`; each rectangle uses top-left `x, y` plus `width, height`.
- Clip **each rectangle separately**. Its clipped bounds are:
  `left=max(0,x)`, `top=max(0,y)`, `right=min(W,x+width)`, `bottom=min(H,y+height)`.
  Its visible area is `max(0,right-left) * max(0,bottom-top)`.
- For clipped rectangles A and B, intersection area is
  `max(0,min(A.right,B.right)-max(A.left,B.left)) * max(0,min(A.bottom,B.bottom)-max(A.top,B.top))`.
  **Union area = area(A) + area(B) − intersection area**; do not use the area of their enclosing bounding box. Fully off-screen rectangles and edge-only contact contribute zero area.
- `impact_fraction = union_area / (W*H)`.
  Use the **original, unclipped** coordinates for
  `distance_fraction = min(1.0, max(abs(current.x-previous.x), abs(current.y-previous.y)) / max(W,H))`.
  Multiply the unrounded fractions for `score`; round only when writing.
- Iterate over `sorted(data['frames'], key=lambda frame: frame['id'])` for ascending string order. Write with `csv.writer`, header `['id','impact_fraction','distance_fraction','score']`, and format each numeric field as `f'{value:.6f}'`. Check the resulting CSV header and row count after running the script.
