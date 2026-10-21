# Parse a branching dialogue script into a JSON graph

The input `/root/work/script.txt` is a dialogue script divided into sections. Each section begins with a header line `[SectionId]`. The lines that follow it, up to the next header, form the body of that section.

Lines to ignore:
- Blank lines.
- Comment lines, whose first non-space character is `#`.

Every other body line has one of two forms:
- **Speaker line:** `Speaker: text -> Target`. The speaker is everything before the first `:`. The text is everything after that colon and before the arrow.
- **Option line:** `N. option text -> Target`, where `N` is an integer.

In both forms, the target is whatever follows the last `->`. Strip surrounding whitespace from every extracted field.

A section that contains option lines is a `choice` node. Its `speaker` and `text` are both empty strings. Every other section contains exactly one speaker line and is a `line` node, with the speaker and text taken from that line.

The target `End` marks the end of the conversation. No node is created for it.

Write `/root/work/dialogue.json` with this structure:
```
{"start": "<id of first section>",
 "nodes": [{"id": "", "text": "", "speaker": "", "type": "line|choice"}],
 "edges": [{"from": "", "to": "", "text": ""}]}
```

The `nodes` list has one entry per section, in file order.

The `edges` list has one entry per body line, in file order:
- For a speaker line, the edge `text` is `""`.
- For an option line, the edge `text` is the option text with the leading `N.` removed. Keep any bracketed tags such as `[Lie]`.

The output must be valid JSON; key order inside the objects does not matter.
