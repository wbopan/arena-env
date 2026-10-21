1. Inspect `/root/data` with `ls`, then `head -40` and `grep -v '^#' | head` on michigan_stations.txt to learn the format (likely USGS RDB, tab-separated, `#` comments, plus a format row) and find the `00065` gage-height column. Read IDs as strings.
2. Filter to 2025-04-01..07, take the daily max per station (`resample('D').max()`), and use `nwis.get_iv(..., parameterCd='00065')` only if values aren't in the file.
3. Get thresholds from the NWS `nwps_all_gauges_report.csv` (truncate rows to the header length; use the `usgs id` and `flood stage` columns; drop NaN and -9999).
4. Count days with daily_max >= flood stage, keep counts > 0, and write `station_id,flood_days` to `/root/output/flood_results.csv`. Then check the header, leading zeros, and the 1–7 range.
