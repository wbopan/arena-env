**Goal artifacts (exact paths)**
- `/root/output/index.html` is the single page. It loads `js/d3.v6.min.js`, then `js/visualization.js`, plus `css/style.css`. Use relative paths.
- `/root/output/js/d3.v6.min.js` must be a real D3 **v6** bundle, not v7. Do not link a CDN from the page.
- `/root/output/js/visualization.js` and `/root/output/css/style.css`.
- `/root/output/data/` holds a copy of the inputs: `cp -r /root/data/* /root/output/data/`. This gives `data/stock-descriptions.csv` and `data/indiv-stock/…`.

**Getting D3 v6 offline**
1. Search the container first: `find / -name "d3*.min.js" -not -path "*/proc/*" 2>/dev/null | head`. Then check the version with `head -c 200 file`. It should say `// https://d3js.org v6.x`.
2. If you don't find one, try the network:
   - `curl -sL https://d3js.org/d3.v6.min.js -o ...`, or
   - `curl -sL https://unpkg.com/d3@6.7.0/dist/d3.min.js -o ...`, or
   - `npm pack d3@6.7.0`.
3. Verify the download: `head -c 100` should show v6, and `wc -c` should be roughly 260 KB.

**Inspect inputs cheaply**
- `head -3 /root/data/stock-descriptions.csv`
- `wc -l /root/data/stock-descriptions.csv`
- `ls /root/data/indiv-stock | head`
- `python3 -c "import csv;r=list(csv.DictReader(open('/root/data/stock-descriptions.csv')));print(r[0].keys());print(sorted({x['sector'] for x in r}))"`. Adjust the column name to whatever the file actually uses.

Things to learn from this:
- the exact column names (ticker, name, sector, marketCap, country, website, …);
- how ETFs are marked (sector value "ETF" or an empty marketCap);
- that there are 50 rows.

Do not print whole files.

**Data loading pitfall**
- `d3.csv('data/stock-descriptions.csv')` fails under `file://` in some browsers.
- Robust pattern: have the Python build script embed the parsed rows as `const EMBEDDED_DATA = [...]` at the top of visualization.js. Then do `d3.csv('data/stock-descriptions.csv').then(render).catch(()=>render(EMBEDDED_DATA))`.
- Parse marketCap with `+d.marketCap`. Treat empty or NaN as missing (ETF).
- Sort rows deterministically, e.g. by ticker or by market cap descending.

**Layout**
- Wrap the two charts in `<div id="container" style="display:flex">`.
- Left: `<div id="bubble-chart"><svg>`, for example width 600, height 600, with a viewBox.
- Right: `<div id="table-container">` holding `<table id="stock-table">`. Give it `max-height` and `overflow-y:auto` so it sits side by side with the chart.
- Add `<div id="tooltip" class="tooltip"></div>` to the page.

**Bubble chart**
- Radius: `d3.scaleSqrt().domain([0,maxCap]).range([8,50])` for stocks. ETFs get a fixed radius, e.g. 18.
- Colour: `d3.scaleOrdinal(d3.schemeTableau10).domain(sectors)`, where `sectors` is sorted.
- Cluster centres: lay the sectors out compactly around the chart centre, e.g. on a small circle of radius about 150px, or in a 3×3 grid within the inner region.
- Force simulation (deterministic, no `Math.random`):
```js
nodes.forEach((d,i)=>{d.x=cx[d.sector]+(i%5)*3; d.y=cy[d.sector]+Math.floor(i/5)*3;});
const sim=d3.forceSimulation(nodes)
 .force('x',d3.forceX(d=>cx[d.sector]).strength(0.15))
 .force('y',d3.forceY(d=>cy[d.sector]).strength(0.15))
 .force('collide',d3.forceCollide(d=>d.r+2).iterations(3))
 .stop();
for(let i=0;i<300;i++) sim.tick();
nodes.forEach(d=>{d.x=Math.max(d.r,Math.min(W-d.r,d.x)); d.y=Math.max(d.r,Math.min(H-d.r,d.y));});
```
  You may add a weak `forceCenter` or extra x/y forces toward the centre so clusters stay near the middle.
- Each bubble is a `g.bubble` holding a `circle` (with `attr('data-ticker', d.ticker)`, class `bubble`) and a `text` showing the ticker. The text is centred with `text-anchor:middle` and `dominant-baseline:central`, sized to fit the radius, and has `pointer-events:none`.
- Legend: one coloured rect or circle plus the sector name per sector (`g.legend`). Place it in a corner of the SVG or just below it.

**Tooltip**
- Follow the skill pattern: `.tooltip{position:absolute;opacity:0;pointer-events:none;...}` and `.tooltip.visible{opacity:1}`.
- On mouseover, if the item is an ETF, `return` early. Otherwise set `.classed('visible',true)`. The html must show ticker, name, and sector, positioned with `event.pageX+10` / `event.pageY-10`.
- On mouseout, set `classed('visible',false)`.
- D3 v6 handler signature is `(event, d)`.

**Table**
- Header: `<th>`Ticker symbol, Full company name, Sector, Market cap, in exactly that wording.
- One `<tr data-ticker=...>` per stock, 50 rows in total.
- Market cap formatting: `d3.format('.3s')(v).replace('G','B')` gives "1.64T" or "512B". ETFs show "N/A" or "—".

**Linked highlight**
```js
function select(t){
 d3.selectAll('circle.bubble').classed('selected',d=>d.ticker===t);
 d3.selectAll('#stock-table tbody tr').classed('selected',d=>d.ticker===t);
 const row=document.querySelector(`tr[data-ticker="${t}"]`); if(row) row.scrollIntoView({block:'nearest'});
}
```
- Attach `on('click',(e,d)=>select(d.ticker))` to both the circles and the rows.
- CSS: `circle.selected{stroke:#000;stroke-width:3px}` and `tr.selected{background:#ffe08a}`.
- No transitions are needed.

**Step plan**
1. Inspect the CSV header, sectors and ETF rows (one or two commands). Run `mkdir -p /root/output/{js,css,data}`.
2. Obtain d3.v6.min.js and verify its version. Copy the data.
3. Write one Python build script that:
   - reads the CSV;
   - writes index.html, style.css, and visualization.js (with embedded JSON data plus the d3.csv fallback).

   Use a heredoc with `cat > build.py <<'EOF'`.
4. Run the script. Then check:
   - `ls -R /root/output | head`;
   - `grep -c "forceCollide\|forceX\|forceY" js/visualization.js`;
   - `node -e "require('fs').readFileSync(...)"` or `node --check /root/output/js/visualization.js` for a syntax check;
   - the head of index.html.
5. If Playwright or Chromium is available, smoke-test the page. Confirm:
   - 50 circles and 50 table rows;
   - the tooltip is hidden for ETFs;
   - clicking a bubble highlights its row, and vice versa.

   Serve with `python3 -m http.server` from /root/output, or rely on the embedded fallback.
