1. Cat `ada_rules.json`, `layer_schema.json` and `/root/output_schema/*`. Use ezdxf to count entities per layer, then dump WALL/DOOR/fixture/grab-bar/clearance geometry compactly.
2. Room = inner WALL faces (lower interior band at top) plus the door-wall plane at bottom. Use tight fixture bboxes; door width = opening segment.
3. In one script, check the rules (exact rule names; WC1 for centerline, bathroom_1 for circle fit) with Shapely: inset room by the offset, subtract the tub, test a 60" circle.
4. Repair locally: outward door, toilet center 17" from the side wall, grab bars ≥42/≥36 tied to the toilet, lav knee clearance declared, circle placed. Write the five JSONs plus `repaired_plan.dxf` with REPAIR-* layers to `/root/output/`.
5. Reload the outputs to verify JSON/DXF agreement and that all checks pass.
