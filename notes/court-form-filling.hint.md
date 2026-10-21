1. Dump every widget in `/root/sc100-blank.pdf` with pypdf as one line each (page, short full name, `/FT`, `/TU` tooltip, `/AP` states) into a file, then grep it to map fields to SC-100 items 1–11.
2. Write one pypdf script that fills only these fields, with dates as 2025-09-30, 2026-01-19 and filing date 2026-01-19:
   - plaintiff and defendant info, amount 1500, reason, the start/through dates and how calculated;
   - checkboxes: Yes for "asked to pay", 5(a)(1) "defendant lives", zip 94086, No for items 7–10;
   - signature date and typed name.
3. For checkboxes, set `/V` and `/AS` to each widget's own on-state. Call `set_need_appearances_writer(True)`, drop XFA, and save to `/root/sc100-filled.pdf`.
4. Re-read the output with `get_fields()` and confirm only those fields are non-empty.
