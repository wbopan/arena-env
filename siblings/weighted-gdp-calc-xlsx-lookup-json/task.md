# GCC net exports in percent of GDP

The workbook `/root/work/gdp.xlsx` contains a sheet named `Data` with annual national-accounts series for the six GCC countries, in USD millions. Row 1 is a title and row 2 is a source note. The header row has the columns `Country`, `Series Code`, `Series Name`, followed by one column per year. Each data row below the header is one series for one country. The rows are not in any particular order.

A series code is a 3-digit country prefix followed by a series suffix:
- `NGDPD.A`: GDP, current prices
- `BXGS_BP6.A`: exports of goods and services
- `BMGS_BP6.A`: imports of goods and services

The sheet also contains other series, which are not needed.

For every country and every year present in the header, compute net exports as a percentage of GDP:

`NX% = (Exports - Imports) / GDP * 100`

For each year, also compute the GCC GDP-weighted mean of NX%. Use each country's share of the summed GDP of the six countries in that year as its weight.

Write the results to `/root/work/nx_gdp.json` with this structure:

```json
{"countries": {"<Country name as in column A>": {"<year>": <NX%>, ...}, ...},
 "gcc_weighted": {"<year>": <weighted NX%>, ...}}
```

Requirements:
- Year keys are strings such as `"2018"`.
- All values are in percent, rounded to 2 decimals.
- Compute the weighted means from the unrounded country values.
- Do not modify `gdp.xlsx`.
