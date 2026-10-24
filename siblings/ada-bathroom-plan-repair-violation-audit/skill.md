## Reference notes

Use Python’s standard library for the ASCII DXF and JSON. **Inspect `ada_rules.json` before coding comparisons**: take thresholds, `wall_offset`, `blocking_layers`, rule names, and reported element IDs from the file rather than assuming a schema or default values.

### Read the DXF cheaply

ASCII DXF consists of alternating *group-code* and *value* lines. Restrict extraction to the `ENTITIES` section; a `0` group starts each entity. Relevant codes: `8` layer; `10,20` LINE start or CIRCLE center; `11,21` LINE end; `40` CIRCLE radius.

```python
from pathlib import Path
import json, math

lines = Path("/root/work/ada_bath_plan.dxf").read_text().splitlines()
pairs = [(int(lines[i].strip()), lines[i+1].strip())
         for i in range(0, len(lines)-1, 2)]

# First collect groups between SECTION / ENTITIES and ENDSEC.
# Then split that section at each group code 0; retain LINE and CIRCLE.
# A simple dict of an entity's groups works for these entity types.
```

A quick inventory of `(layer, entity type)` counts and LINE coordinates helps identify the wall faces without dumping the whole file. Ignore TEXT and ARC for the requested measurements.

### Geometry and checks

- **Room:** report the axis-aligned rectangle bounded by the *inner* `WALL` faces, not the outer faces or wall centerlines. The bottom inner face is interrupted by the door; use its shared wall plane as `ymin`.
- **Door:** use the horizontal `DOOR` LINE; its endpoint distance is the clear width. Ignore the leaf and swing.
- **Fixtures:** each `WC` and `TUB` bbox is the min/max of **LINE endpoint coordinates only** on that layer.
- **Bars:** classify `GRABBAR` LINEs by orientation. Vertical = side bar; horizontal = rear bar. Length is `math.hypot(x2-x1, y2-y1)`.
- **Toilet:** `cx = (wc_xmin + wc_xmax)/2`; centerline distance is `min(cx-room_xmin, room_xmax-cx)`. Rear-bar span passes when `min(bar_x1,bar_x2) <= cx <= max(bar_x1,bar_x2)`.
- **Turning circle:** diameter is `2*radius`. For center `(cx,cy)` and radius `r`, containment with inclusive touching requires:
  ```python
  xmin + offset <= cx-r and cx+r <= xmax-offset
  ymin + offset <= cy-r and cy+r <= ymax-offset
  ```
  For each fixture bbox on `blocking_layers`, find its nearest point to the circle center:
  ```python
  nx = max(bx0, min(cx, bx1))
  ny = max(by0, min(cy, by1))
  overlaps = (cx-nx)**2 + (cy-ny)**2 < r**2
  ```
  Strict `<` means tangency passes. Circle fit passes only if containment passes **and** no blocking bbox overlaps.

Compare every rule using its JSON thresholds; minimum and maximum bounds are inclusive. Include one `{"rule": name, "element": configured_id}` per failed rule, sorted by rule name. Round numeric output to three decimals **when writing JSON**, not before comparisons. A compact workflow is: inspect rule keys and layer inventory → extract geometry → evaluate each listed rule → write `/root/work/ada_check.json` → read it back to confirm the required keys and sorted violations.
