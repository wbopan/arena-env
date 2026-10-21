The deck `/root/work/deck.pptx` has paper titles left as dangling text boxes. A **dangling title** is any shape that is not a placeholder, has a text frame with non-empty text, and whose whitespace-trimmed text does not start with `Note:`. Note boxes must be left exactly as they are (text, position, size).

Process the deck and save the result as `/root/work/deck_processed.pptx`:

1. For every dangling title, set every run to font Arial, size 16 pt, color #989596, bold off, and set every paragraph's alignment to center. Do not change the text.
2. Reposition and resize every dangling title box so it spans the bottom of its slide: left = 0.5 in, width = slide width - 1 in, height = 0.5 in, top = slide height - 0.75 in (1 in = 914400 EMU).
3. Append one new slide at the end using the deck's "Title and Content" layout. Its title placeholder text is exactly `Reference`. Its body placeholder (idx 1) holds the unique paper titles, one paragraph per title, in order of first appearance (slide order, then shape order within a slide). Two titles are duplicates if they are equal ignoring case after collapsing whitespace; keep the text of the first occurrence. Each body paragraph must use PowerPoint automatic numbering (`a:buAutoNum`) of type `arabicPeriod`, and the body must contain no other non-empty paragraphs.

Keep all existing slides in their original order and do not add or remove any other shapes.
