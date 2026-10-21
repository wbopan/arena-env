# ADA plan-view violation audit

Inputs in `/root/work`:

- `ada_bath_plan.dxf`: an ASCII DXF of one toilet room. All units are inches. The ENTITIES section contains LINE, CIRCLE, ARC and TEXT entities.
- `ada_rules.json`: rule names, thresholds, and the element id that each rule is reported against.

Layer conventions:

- `WALL`: each wall is drawn as two parallel LINEs 6 in apart, one for the outer face and one for the inner face. The room interior is the axis-aligned rectangle bounded by the inner faces. The bottom (lowest-y) wall is interrupted by the door opening.
- `DOOR`: the horizontal LINE is the clear opening, and its length is the door clear width. Ignore the leaf line and the swing arc.
- `WC` and `TUB`: a fixture's bbox is the extent of the LINE endpoints on its layer. Other entity types on these layers are decorative.
- `GRABBAR`: the vertical LINE is the side-wall bar and the horizontal LINE is the rear-wall bar. Bar length is the segment length.
- `CLEARANCE`: the CIRCLE is the wheelchair turning space.

Rule semantics:

- All min/max thresholds are inclusive.
- Toilet centerline is the horizontal distance from the WC bbox center x to the nearer of the left and right interior faces.
- `rear_grab_bar_toilet_centerline_span` passes if the toilet center x lies within the rear bar's x-range.
- `turning_circle_fit_usable_floor` passes only if both conditions hold:
  - The whole circle lies inside the interior rectangle shrunk by `wall_offset` on every side. Touching is allowed.
  - The circle does not overlap the bbox of any fixture on `blocking_layers`. Tangency is allowed.

Write `/root/work/ada_check.json` in this form:

```
{"room": {"xmin": .., "ymin": .., "xmax": .., "ymax": ..},
 "measurements": {"door_clear_width": .., "toilet_centerline_from_side_wall": .., "side_grab_bar_length": .., "rear_grab_bar_length": .., "turning_circle_diameter": ..},
 "violations": [{"rule": "<rule name>", "element": "<element id from rules>"}]}
```

Output requirements:

- All numbers are in inches, rounded to 3 decimals.
- `violations` contains exactly one entry per failed rule, sorted by rule name.
- If no rule fails, `violations` is an empty list.
