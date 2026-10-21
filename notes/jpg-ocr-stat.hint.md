1. Run `ls`/`wc` on `/app/workspace/dataset/img`. OCR one sample with `pytesseract.image_to_string` and print only the lines containing TOTAL, AMOUNT or date-like patterns.
2. Write one script that OCRs every image in sorted order (caching the text). Extract the date with day-first regexes, validated and output as ISO. Extract the total using the keyword priority groups, the exclusion list, the last `\d+.\d{2}` on the line (commas stripped), and the next-line fallback. Missing values become None.
3. Save with openpyxl to `/app/workspace/stat_ocr.xlsx`: one sheet `results`, header `filename,date,total_amount`, amounts as `"%.2f"` strings.
4. Verify the sheet name, row count, sort order and value formats, inspect the None rows, tune, then evaluate.
