1. Find the source directory, then count files by extension with `find $D -type f | sed 's/.*\.//' | sort | uniq -c`; check which of pdftotext, pandoc, python-docx and python-pptx are available.
2. In one Python script, extract the first ~3 pages or slides of text per file (pdftotext/pypdf, python-docx/pandoc, python-pptx) and score keywords for the 5 subjects. Use specific terms: qubit/trapped ion, black hole/horizon, DNA/genome, composer/music, language model/LLM.
3. Do a dry run to `/tmp/plan.json`, review only the ambiguous or zero-text files, and send no-match files to `music_history`.
4. Move the files unchanged into `$D/{LLM,trapped_ion_and_qc,black_hole,DNA,music_history}`.
5. Verify zero files are left at the top level of `$D` and the five folder counts sum to the original total.
