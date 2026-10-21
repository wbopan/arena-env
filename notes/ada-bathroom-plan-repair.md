**Inputs and first look (keep output small).**
- `ls /root/input /root/output_schema`.
- `cat` the small JSONs: `ada_rules.json` (rule names, minimums, wall offset, which fixtures may overlap the turning circle) and `layer_schema.json` (layer aliases).
- `cat /root/output_schema/*.json` or a schema summary, so the top-level keys you write match exactly.
- Ignore the screenshot. The DXF is authoritative and in inches; check `doc.header.get('$INSUNITS')` but do not convert.

Layer inventory one-liner:
```python
import ezdxf,collections
doc=ezdxf.readfile('/root/input/ada_bath_input.dxf'); msp=doc.modelspace()
c=collections.defaultdict(collections.Counter)
for e in msp: c[e.dxf.layer][e.dxftype()]+=1
print(dict(c))
```

Then dump compact geometry per layer, rounded to 2 decimals:
- `LINE`: `e.dxf.start`, `e.dxf.end`.
- `LWPOLYLINE`: `e.get_points('xy')`, `e.closed`.
- `CIRCLE` / `ARC`: `center`, `radius`, `start_angle`, `end_angle`.
- `SPLINE`: `control_points` or `fit_points`.
- `TEXT` / `MTEXT`: `e.dxf.text` / `e.text`.

Print WALL lines sorted, and the other layers one at a time if they are large. Dimension and annotation text may state the door width, the lavatory knee clearance and other metadata.

**Room polygon (extracted).** Build an axis-aligned rectangle from the inside faces of the WALL lines:
- left = inner vertical face of the left wall; right = inner vertical face of the right wall.
- top = the lower continuous horizontal interior wall line bounding the toilet/lav/tub zone, not an upper service band.
- bottom = the door-wall plane the door opening sits on, not a short raised return above the threshold.
- Sanity check: every fixture bbox must lie inside it.
- Never use the outer envelope, wall centerlines, the clearance polyline or a fixture envelope.
- Write the polygon ordered, for example `[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]`.
- In `layer_inventory.json`, note "no SPACE layer; room derived from WALL inner faces + door-wall plane", plus the alias mapping and entity counts and types per layer.

**Fixtures.** Produce one object each for WC1 (toilet), LAV1 (lavatory) and TUB1 (bathtub), each with a tight bbox of the primary body.
- Drop arcs whose radius is more than 1.5× the body extent, or whose center lies outside the dense cluster for that layer.
- Lavatory: use the outer basin/counter/apron body. Exclude flanking arcs, side returns and knee-clearance graphics. Do not shrink it to the inner bowl.
- Lavatory knee/toe clearance comes from drawn or annotated metadata (`knee_toe_clearance`, `knee_clearance {width, depth}`).

**Door D1.**
- Clear width = length of the opening segment (jamb to jamb), not the leaf arc.
- Swing direction comes from the arc position: an arc inside the room means inward.
- Record the opening segment endpoints.

**Grab bars.**
- Classify by orientation. A bar parallel to and near a side wall is GB_SIDE; a bar on the wall behind the toilet is GB_REAR.
- Length = segment length; report endpoints. Paired offset lines → use the center segment.
- Missing bars are a violation; add them in the repair.

**Rule checks** (use the exact rule names from `ada_rules.json`; one entry per failed rule/element):
- **door_clear_width_min**: width ≥ 32. Element D1.
- **Door swing conflict**: test the swing sector polygon (Shapely) against WC/LAV/TUB bboxes and the clear-floor rectangles.
- **toilet_centerline_from_side_wall_range**: distance from the WC bbox center x (or y) to the nearest room side wall must be 16–18. Report the single combined range rule on WC1; never split into min/max.
- **turning_circle_fit_usable_floor**: element `bathroom_1`.
  - usable = room polygon `.buffer(-offset)` (offset from the rules), minus the tub and any non-overlappable fixtures.
  - The lavatory is subtracted only if knee clearance is not declared. Toilet clear floor space may overlap.
  - Test `usable.contains(Point(c).buffer(30))`.
  - Grid-search the center at 0.5" steps over the room to see whether any position fits.
- **turning_circle_diameter_min**: the diameter must be ≥ 60. A drawn circle that is smaller is a violation.
- **side_grab_bar_length_min** (≥ 42) and **rear_grab_bar_length_min** (≥ 36).
- **side_grab_bar_toilet_side_wall_alignment**: the side bar must be on the same wall used for the centerline and overlap the toilet's extent along that wall.
- **rear_grab_bar_toilet_centerline_span**: the rear bar must lie on the toilet's rear wall and its span must include the toilet centerline coordinate.
- **lavatory_knee_clearance_min**: report only if the clearance is missing or below 30 wide × 19 deep.
- Report only rules that actually fail. Use no vertical rules (heights, seats, mirrors, pipes).

**Repair, minimal changes.**
1. Set the door swing to `"outward"` (or sliding). Widen the opening only if it is under 32.
2. Move only the toilet so its center is ~17" from the adjacent side wall. Do not move the tub; move the lav locally only if needed.
3. Re-place GB_SIDE (≥ 42, on the same side wall, overlapping the toilet) and GB_REAR (≥ 36, on the rear wall, spanning the new centerline). Keep both coordinated with the moved toilet.
4. Declare lav `knee_toe_clearance: true` and `knee_clearance {width ≥ 30, depth ≥ 19}`.
5. Place a 60" turning circle at a center that passes the usable-floor check.
6. Keep the room unchanged.
7. Recompute every check in the script and assert they pass.
8. The declared `centerline_from_side_wall` must equal the geometric distance computed from the bbox.

**Repaired DXF.** Re-read the input to keep the context, add layers, and draw:
```python
for L in ['REPAIR-ROOM','REPAIR-DOOR','REPAIR-WC','REPAIR-LAV','REPAIR-TUB','REPAIR-GRABBAR','REPAIR-CLEARANCE']:
    if L not in doc.layers: doc.layers.add(L)
msp.add_lwpolyline(pts, close=True, dxfattribs={'layer':'REPAIR-WC'})
msp.add_line(p1,p2,dxfattribs={'layer':'REPAIR-GRABBAR'})
msp.add_circle(c,30,dxfattribs={'layer':'REPAIR-CLEARANCE'})
doc.saveas('/root/output/repaired_plan.dxf')
```
- REPAIR-ROOM: room rectangle.
- REPAIR-WC / REPAIR-LAV / REPAIR-TUB: fixture bboxes.
- REPAIR-DOOR: opening line, plus an outward arc if you like.
- REPAIR-GRABBAR: two lines.
- REPAIR-CLEARANCE: turning circle, plus the 30×48 lav-front clear floor rectangle.
- All geometry must be identical to `repaired_layout.json`.

**JSON outputs** in `/root/output/`; follow the `/root/output_schema` keys exactly, with `unit: "inches"` and coordinates rounded to 3 decimals everywhere:
- `layer_inventory.json`
- `extracted_original_layout.json` (original condition): room, door, fixtures, grab_bars, turning_space.
- `violations_before.json`
- `repaired_layout.json`
- `changes.json`: per edit, the element id, the action, the reason (the rule) and before/after values.

Use the stable IDs everywhere: bathroom_1, D1, WC1, LAV1, TUB1, GB_SIDE, GB_REAR.

**Plan.**
1. Inspect the rules, schema and output schemas.
2. Run the layer inventory.
3. Dump the geometry per layer.
4. Write one script, `/root/solve.py`, that extracts, checks, repairs, re-checks and writes all files.
5. Run it.
6. Validate: `json.load` each file; re-read `repaired_plan.dxf` and confirm the REPAIR-* entities match the JSON; confirm with Shapely that fixtures are inside the room and the circle fits.
7. Optionally use matplotlib for `screenshot_after.jpg`, showing the 30×48 lav rectangle.
