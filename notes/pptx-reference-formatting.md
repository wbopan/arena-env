**Tools.** Use `python-pptx` (`from pptx import Presentation`) for all reading and editing. It is simpler than unpacking the XML. Use raw lxml through `paragraph._p` only for numbered bullets. For a quick text overview, run `python -m markitdown /root/Awesome-Agent-Papers.pptx | head -80`. Do not print whole files.

**Step 1: Inspect cheaply.** Run a one-liner that lists every shape on every slide:

```python
from pptx import Presentation
p=Presentation('/root/Awesome-Agent-Papers.pptx')
print(p.slide_width,p.slide_height,[l.name for l in p.slide_layouts])
for i,s in enumerate(p.slides):
  for sh in s.shapes:
    ph=sh.placeholder_format.type if sh.is_placeholder else None
    print(i,sh.shape_id,sh.name,ph,sh.left,sh.top,sh.width,sh.height,repr(sh.text_frame.text[:70]) if sh.has_text_frame else '')
```

**What counts as a "dangling paper title".** It is a text shape that is not the slide's title or body placeholder. It is usually a free text box (`placeholder None`, name like "TextBox N"). Its text is a single paper title, often placed oddly or wrapped onto several lines.
- Confirm the pattern from the listing: which slides have one, and whether some slides have none.
- Do not touch real title or body placeholders.
- A title may repeat across slides. Keep each occurrence on its slide, but deduplicate for the Reference slide.
- Strip whitespace when comparing. Normalize internal newlines and vertical tabs to spaces, because a wrapped title may contain line breaks.

**Step 2: Format each dangling title.** Apply to every paragraph and every run:

```python
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
tf=sh.text_frame
for para in tf.paragraphs:
    para.alignment=PP_ALIGN.CENTER
    for r in para.runs:
        f=r.font; f.name='Arial'; f.size=Pt(16); f.bold=False
        f.color.rgb=RGBColor(0x98,0x95,0x96)
```

If the original text has line breaks, collapse it to one paragraph first: `tf.text = ' '.join(title.split())`. Then re-apply the formatting above, because setting `tf.text` resets the runs.

**Step 3: Make each title fit on one line.**
- Set `tf.word_wrap=False`, which writes `wrap="none"`.
- Set `tf.auto_size=MSO_AUTO_SIZE.NONE`.
- Set the box width to the estimated text width plus the insets.
- Measure the width with PIL if an Arial-like TTF exists (`fc-list | grep -i -E "arial|liberation"`):

```python
from PIL import ImageFont
font=ImageFont.truetype(path,16)
w_pt=font.getlength(text)   # 16px font → width in pt at 16pt
```

- Fallback when no font is found: `w_pt ≈ 0.55*16*len(text)`.
- Compute `width = Emu(int((w_pt+ 20) * 12700))`; this adds a margin covering the default 0.1" insets.
- Cap the width at `slide_width`.
- Use a height of about `Pt(16*1.2) + insets`, roughly `Emu(400000)`.

**Step 4: Place each title at the bottom center.**

```python
sh.left = int((p.slide_width - sh.width)/2)
sh.top  = int(p.slide_height - sh.height - Emu(100000))   # small bottom margin, stays inside slide
```

Keep the paragraph alignment CENTER. The box must lie fully inside the slide and be horizontally centered: `left + width/2 == slide_width/2`, within rounding.

**Step 5: Build the Reference slide at the end.**
- Collect the titles in order of first appearance, deduplicated after normalization (a `seen` set).
- Pick a layout that has both a title and a body placeholder, usually "Title and Content" (`p.slide_layouts[1]`). Verify it by name or by its placeholders.

```python
s=p.slides.add_slide(layout)
s.shapes.title.text='Reference'
body=[ph for ph in s.placeholders if ph.placeholder_format.idx!=0][0]
tf=body.text_frame; tf.clear()
from pptx.oxml.ns import qn
from lxml import etree
for k,t in enumerate(titles):
    para=tf.paragraphs[0] if k==0 else tf.add_paragraph()
    para.text=t
    pPr=para._p.get_or_add_pPr()
    for tag in ('a:buNone','a:buChar','a:buAutoNum'):
        for e in pPr.findall(qn(tag)): pPr.remove(e)
    pPr.set('marL','342900'); pPr.set('indent','-342900')
    etree.SubElement(pPr, qn('a:buAutoNum')).set('type','arabicPeriod')
```

- `buAutoNum` must come after any `lnSpc`/`spcBef`/`spcAft`/`buClr`/`buSzPct`/`buFont` children in `pPr`. Appending to a fresh `pPr` is fine.
- Never type "1." manually into the text.
- Optionally shrink the font (`run.font.size`) if the list is long, so it fits the body.
- If no suitable layout exists, add a textbox body. Placeholder title plus body is preferred, so the slide title is detectable via `s.shapes.title`.

**Step 6: Save.** Call `p.save('/root/Awesome-Agent-Papers_processed.pptx')`. Do not overwrite the original.

**Step 7: Evaluate.** Reopen the output and print, for each original slide, the dangling shape's properties:
- font name, size, bold, and color of every run (`r.font.color.rgb`);
- `word_wrap` and the `bodyPr` wrap attribute;
- left, top, width, and height against the slide size;
- that the text is a single line with no `\n`.

For the last slide, check:
- the title is "Reference";
- the count of body paragraphs equals the number of unique titles;
- each paragraph's `pPr` contains `buAutoNum`;
- there are no duplicates.

Also confirm:
- the slide count is the original count plus 1;
- non-dangling shapes are unchanged.

For an optional visual check, run `soffice --headless --convert-to pdf` then `pdftoppm -png -r 50`. Use this only if the budget allows.

**Pitfalls.**
- Runs with no explicit `rPr` inherit bold from the layout. Explicitly set `bold=False` (writes `b="0"`).
- Color must be RGB `989596`, not a theme color.
- Size 16pt is `sz="1600"`.
- Do not leave `normAutofit` (shrink-on-overflow); use auto_size NONE.
- Keep titles whose text is identical except for whitespace or case as one Reference entry. Match exact text after whitespace normalization; be careful about case.
