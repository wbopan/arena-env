1. Inspect the CSV header, sectors and ETF rows with `head` and a python csv one-liner. Locate a D3 **v6** bundle (`find` / curl unpkg d3@6.7.0) and verify it with `head -c 100`.
2. `mkdir -p /root/output/{js,css,data}`, then `cp -r /root/data/* /root/output/data/`. Write one Python script that generates index.html (flex side-by-side layout, tooltip div), css/style.css and js/visualization.js with embedded data plus a d3.csv fallback.
3. Bubble chart: scaleSqrt by marketCap with a fixed ETF radius, ordinal colour by sector, forceX/forceY toward compact central sector centres, forceCollide(r+2), run 300 manual ticks, ticker labels, legend, and no tooltip for ETFs.
4. Table: 50 rows with columns Ticker symbol / Full company name / Sector / Market cap (`d3.format('.3s')` with G→B). A shared `select(ticker)` toggles the `.selected` class on both circles and rows.
5. Validate with `node --check`, grep for the forces, count the rows, and optionally do a headless browser smoke test.
