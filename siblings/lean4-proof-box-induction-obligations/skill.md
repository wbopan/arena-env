## Reference notes

The Lean proof tools in the supplied documents are not needed here. Use Python’s standard-library `json` module and built-in integers for exact arithmetic.

- Read the input array with `json.load(open("/root/work/recurrences.json"))`. Preserve its order.
- For an inclusive box `[xmin, xmax, ymin, ymax]`, membership means `xmin <= x <= xmax and ymin <= y <= ymax`. Check the initial state independently of the closure obligation.
- The transition is affine: `(a*x + b*y + c, d*x + e*y + f)`. Each output coordinate reaches its minimum and maximum over a rectangular box at corners. Thus, checking the four corners suffices to decide whether **every** state maps into the box; do not enumerate the entire box.
- For a failed closure check, consider corners in lexicographic order: `(xmin, ymin)`, `(xmin, ymax)`, `(xmax, ymin)`, `(xmax, ymax)`. The first whose image is outside the box is the witness. Equal bounds may repeat a corner; this does not affect the result.
- Set `induction_ready` only when both independent obligations hold. Python `bool` and `None` serialize as JSON booleans and `null`; a witness should be a two-element integer **list**.
- Write the resulting array with `json.dump(results, open("/root/work/obligations.json", "w"))`. Inspect the input shape briefly before scripting, then run the script and check that the output parses and has one object per input problem with exactly the requested fields.
