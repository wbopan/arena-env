# Build a subject manifest for a messy inbox

The folder `/root/work/inbox/` contains a mix of `.pdf`, `.docx` and `.pptx` files with uninformative names. Each document belongs to exactly one of five subjects. Classify every file by its text content and write a manifest. Do not move, rename or modify the inbox files.

Subject keywords (exact, case-insensitive, whole-word matches; a word is a maximal run of letters a-z):

- `LLM`: transformer, token, prompt, finetuning, attention
- `trapped_ion_and_qc`: ion, qubit, laser, entanglement, trap
- `black_hole`: horizon, accretion, schwarzschild, hawking, singularity
- `DNA`: nucleotide, helix, genome, polymerase, sequencing
- `music_history`: baroque, symphony, composer, opera, renaissance

Use all text in the document: all PDF pages, all docx body paragraphs, and all text on all pptx slides. Count every keyword occurrence for each subject. A file's subject is the one with the highest total. If there is a tie, pick the subject name that is alphabetically first.

Also report `units` for each file:

- PDF: the number of pages.
- pptx: the number of slides.
- docx: the number of body paragraphs whose text is non-empty after stripping whitespace.

Output: `/root/work/manifest.csv`, comma-separated, with the header line `file,subject,units`.

- Include one row per inbox file.
- `file` is the bare filename, for example `scan_123.pdf`.
- `subject` is one of the five names exactly as written above.
- `units` is an integer.
- Sort the rows by `file` in ascending order.
