The deck `/root/work/slides.pptx` contains paper citations placed as loose ("dangling") text boxes on its slides. Build a deduplicated reference index from it.

Definitions:
- A **citation** is a shape that is not a placeholder, has a text frame, and in which every run containing non-whitespace text is italic (run-level italic explicitly true). Whitespace-only runs are ignored. Text inside placeholders (slide titles, bodies, subtitles) never counts, even if italic. A text box with any non-italic, non-whitespace run is not a citation.
- The **citation text** is the concatenation of the box's runs within each paragraph, with paragraphs joined by a single space. Leading and trailing whitespace is removed and every internal run of whitespace is collapsed to one space.
- Two citations refer to the same paper if their citation texts are equal ignoring case.

Order the papers by first appearance: slide order (slide 1 first), then shape order within the slide's shape tree. For each paper, keep the citation text of its first occurrence.

Write `/root/work/references.json` with exactly this structure:

```
{"references": [{"number": 1, "title": "...", "slides": [2, 7]}, ...]}
```

- `number`: 1-based position in the list (integer)
- `title`: first-occurrence citation text (string)
- `slides`: sorted, unique, 1-based slide numbers on which the paper appears as a citation (list of integers)

List only papers that appear as citations. Do not include any other entries.
