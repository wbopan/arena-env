## Reference notes

Use Python’s standard-library `re` and `json`. The skill’s `dialogue_graph` serializer uses `source`/`target` edge keys, while this task requires `from`/`to`; constructing the required dictionaries directly avoids a format mismatch.

- Read `/root/work/script.txt` in order. A header matches a whole line such as `[SectionId]`; its ID is the first section’s `start` if it appears first.
- Ignore empty lines and lines where `line.lstrip().startswith("#")`.
- For each body line, split at the **last** arrow: `content, target = line.rsplit("->", 1)`. Strip both parts. This preserves arrows within dialogue or option text.
- An option prefix can be parsed with `re.fullmatch(r"\s*\d+\.\s*(.*?)\s*", content)`; group 1 is the edge text, including any tags such as `[Lie]`. Otherwise, split the speaker line at its **first** colon: `speaker, text = content.split(":", 1)`, then strip both.
- Preserve section order in `nodes` and body-line order in `edges`. An option-containing section is a `choice` node with empty `speaker` and `text`; otherwise it is a `line` node using its speaker line. Include edges targeting `End`, but do **not** create an `End` node.
- Write the exact requested shape with `json.dump(data, file, ensure_ascii=False, indent=2)`. JSON object key order is immaterial.

A compact workflow: inspect a few lines and section headers, write one parser that accumulates each section’s lines before emitting its node, run it, then read the resulting JSON and check the first section ID, node/edge counts, ordering, and an `End` edge.
