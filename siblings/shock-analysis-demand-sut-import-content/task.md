# Import content of investment from a supply-use table

A small open economy is planning a large investment programme. To estimate how much investment demand leaks into imports, compute the import content of gross fixed capital formation (GFCF) from the national supply-use table.

Input: `/root/work/sut.xlsx` has two sheets, `SUPPLY` and `USE` (million GEL, current prices). In each sheet:
- row 1 is a title and row 2 is blank;
- row 3 holds the column headers;
- product rows start at row 4, each identified by a product code in column A (e.g. `P07`).

The last row has code `TOTAL` and is not a product. Both sheets list the same products by code.

For every product p:
- import ratio r_p = `Imports CIF` / `Total supply at purchasers prices`, both taken from SUPPLY;
- GFCF_p = the value in the `Gross fixed capital formation` column of USE (a blank cell counts as 0).

Compute:
- `import_content_share` = sum over products of GFCF_p * r_p, divided by the sum over products of GFCF_p;
- `gfcf_total` = sum over products of GFCF_p (million GEL);
- `top_import_contributor` = the code of the product with the largest GFCF_p * r_p;
- `import_ratios` = an object that maps every product code to its r_p.

Write `/root/work/import_content.json` as a JSON object with exactly these four keys:
- write ratios and the share as decimals (not percent), rounded to 6 decimals;
- round `gfcf_total` to 1 decimal;
- write product codes exactly as they appear in column A.
