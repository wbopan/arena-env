## Reference notes

Use **python-pptx** to edit the existing deck; use its OOXML helpers for automatic numbering. Iterate `prs.slides` and each slide’s `shapes` in their existing order. A qualifying shape satisfies:

```python
not shape.is_placeholder and shape.has_text_frame
and shape.text.strip()
and not shape.text.strip().startswith("Note:")
```

The `Note:` check is case-sensitive. Do not touch note boxes. Record each qualifying shape’s **original** `shape.text` before formatting it. For uniqueness, use `' '.join(text.split()).casefold()` as the key; retain the first occurrence’s original text.

Useful imports and conventions:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
```

- `prs = Presentation(input_path)`; `prs.slide_width` and `prs.slide_height` are EMU lengths. `Inches(0.5)` and `Inches(0.75)` can be used directly in geometry calculations.
- Set `shape.left`, `.top`, `.width`, `.height` on the **existing** shape; do not replace it.
- For each `shape.text_frame.paragraphs`, set `paragraph.alignment = PP_ALIGN.CENTER`. For **every** `paragraph.runs`, set `run.font.name = "Arial"`, `.size = Pt(16)`, `.color.rgb = RGBColor(0x98, 0x95, 0x96)`, and `.bold = False`. Editing runs this way preserves their text.
- Find the layout by name, e.g. `next(layout for layout in prs.slide_layouts if layout.name == "Title and Content")`; append with `prs.slides.add_slide(layout)`. Use `slide.shapes.title` for the title and `slide.placeholders[1]` for the body (the latter indexes by placeholder **idx**, not shape order).

For the reference body, `body.text_frame.clear()` leaves one empty paragraph. Fill that paragraph with the first title, then call `text_frame.add_paragraph()` for subsequent titles. Do not put literal number prefixes in paragraph text.

PowerPoint automatic numbering requires an OOXML `<a:buAutoNum type="arabicPeriod"/>` inside **each** paragraph’s `<a:pPr>`; text such as `"1. Title"` is not equivalent. With a python-pptx paragraph `p`:

```python
pPr = p._p.get_or_add_pPr()
for child in list(pPr):
    if child.tag.rsplit("}", 1)[-1] in ("buNone", "buChar", "buAutoNum", "buBlip"):
        pPr.remove(child)
num = OxmlElement("a:buAutoNum")
num.set("type", "arabicPeriod")
pPr.insert_element_before(num, "a:tabLst", "a:defRPr", "a:extLst")
```

Save with `prs.save(output_path)`. A quick post-save read can confirm slide count, slide order, reference placeholder contents, and that note boxes retained their text and geometry.
