1. `grep` /app for `localStorage`/`useEffect`/`setTimeout`/`<img`/font imports/skeletons to find each layout-shift and flicker source; view only the relevant line ranges.
2. Fix theme flicker with an inline `<head>` script plus `suppressHydrationWarning`. Use `next/font` (or font-display:swap), and give images explicit width/height.
3. Reserve min-height for late banners and sidebars, match skeleton sizes, and render result/pagination bars immediately; keep all classNames, ids and data-testids unchanged.
4. Run `npm run build && npm start`, then `measure-cls.ts --scroll` (CLS < 0.1) and `detect-flicker.ts` from the browser-testing skill dir; curl the pages and APIs to confirm nothing broke.
