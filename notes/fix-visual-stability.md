**Goal.** Make the Next.js app in `/app` visually stable. That means low CLS, no theme flash, no late content pushing other content, and no hydration flicker. Make the smallest correct edits to the existing components. Never rename or remove existing `className`, `id` or `data-testid` values; hidden tests select on them. Keep every feature working: theme toggle, filters, cart, pagination, API routes.

**1. Inspect cheaply (do not cat whole files).**
- List the source files:
  `cd /app && cat package.json | head -40 && find . -path ./node_modules -prune -o -path ./.next -prune -o -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.css" -o -name "*.js" \) -print`
- Find the suspicious patterns:
  `grep -rn --include=*.tsx --include=*.ts --include=*.css -E "localStorage|useEffect|setTimeout|<img|fonts.googleapis|@import|@font-face|skeleton|Skeleton|min-height|height:|useState\(|Math.random|Date.now|window\.|document\." app components src lib 2>/dev/null | head -80`
- Then view only the relevant line ranges: `sed -n '1,80p' file`.
- Locate the measurement scripts: `find / -name measure-cls.ts -not -path "*/node_modules/*" 2>/dev/null`. The same directory holds `detect-flicker.ts` and `measure.ts`.

**2. Root causes to look for, and their fixes.**

- **Theme read from localStorage in useEffect/useState.** Symptom: a ThemeProvider or wrapper renders light first, then switches to dark. That is a white flash plus a shift.
  - Fix: add a synchronous inline script in the root layout `<head>` that runs before React hydrates and sets the class/attribute on `<html>`. Use the same class or attribute the app already uses.
  - Put `suppressHydrationWarning` on `<html>`.
  - Initialize React state from the DOM lazily: `useState(() => typeof document !== 'undefined' && document.documentElement.classList.contains('dark') ? 'dark' : 'light')`. Alternatively, keep the state but make the CSS depend on the html class so the first paint is already correct.
  - Wrap storage access in try/catch.
  - Do not hide the whole page (e.g. `mounted ? children : null`); that causes a huge shift.

  ```tsx
  <html lang="en" suppressHydrationWarning>
    <head>
      <script dangerouslySetInnerHTML={{ __html:
        `(function(){try{var t=localStorage.getItem('theme');if(t==='dark'){document.documentElement.classList.add('dark');document.documentElement.setAttribute('data-theme','dark')}}catch(e){}})()` }} />
    </head>
  ```

  Match the actual storage key, the class/attribute names, and any wrapper element the app styles (e.g. a body or wrapper `data-theme`).

- **Images without dimensions** (`<img>` without width/height, or containers without a fixed size).
  - Add `width`/`height` attributes plus CSS `aspect-ratio`/fixed height on the container.
  - Or use `next/image` with width/height. With remote URLs you must configure `images.remotePatterns`; for plain `<img>`, keep the same className.

- **Fonts loaded via `<link>` or `@import` (Google Fonts) or `@font-face` without font-display.**
  - Switch to `next/font` (`import { Inter } from 'next/font/google'`, `const inter = Inter({ subsets:['latin'], display:'swap' })`, apply `inter.className` on `<html>`/`<body>`).
  - Or add `font-display: swap`/`optional` and preload.
  - Note: the container may be offline. If so, prefer `next/font/local` or a system font stack with `font-display`. Do not let the build fail.

- **Late banners or promos inserted via setTimeout or a fetch at the top of the page.**
  - Reserve space with a `min-height` equal to the final height (or render a placeholder of the same size from the first render).
  - If it overlays, use position absolute/fixed.

- **Skeleton size mismatch.** Make skeleton cards the same height/width and grid as real cards, and render the same number of them.

- **Late sidebar or filter panel, or a results/pagination bar that appears only after data loads.**
  - Render it immediately with a loading state or fixed width/height. Use a ternary, not `&&`, so no `0` is rendered and no element pops in.

- **Hydration mismatches** (`Math.random`, `Date.now`, `window` reads during render).
  - Make the render deterministic.
  - Move client-only values behind a fixed-size placeholder.

- **Secondary items (only if cheap).** These are good practice but not the main target:
  - Sequential `await`s in pages or API routes → `Promise.all`.
  - Barrel imports → direct imports or `optimizePackageImports`.
  - Long lists → `content-visibility:auto; contain-intrinsic-size`.
  - Animate a wrapper div, not the SVG itself.

**3. Plan.**
1. Run the inspection greps above and note each root cause with its file and line.
2. Edit the files with a small python or `sed` patch script, or rewrite only the affected component files with heredocs. Preserve all existing classNames, ids and data-testids exactly.
3. Build and serve:
   - `cd /app && npm run build 2>&1 | tail -20`
   - then `(npm start > /tmp/srv.log 2>&1 &)`, `sleep 5`
   - Use the dev server if there is no start script. Fix any type or build errors.
4. Verify:
   - `npx ts-node <skilldir>/measure-cls.ts http://localhost:3000 --scroll | head -40`. Target CLS < 0.1 ("good"). Compare against the baseline if you measured before the fix.
   - `npx ts-node <skilldir>/detect-flicker.ts http://localhost:3000`. It must show no white flash with the dark theme stored.
   - Check other routes too (e.g. product list, product detail) with `curl -s localhost:3000/... | head -c 300` and `curl` against the API routes to confirm they still work.
5. Re-grep to confirm the testids/classes are unchanged: `git diff --stat` and `git diff | grep -E "^-.*(data-testid|className|id=)"` should show nothing removed, except where the same value is re-added.

**Pitfalls.**
- Do not print whole files or the build output; pipe through `head`/`tail`.
- The inline script must be a string in `dangerouslySetInnerHTML`, placed in `<head>` of the root `layout.tsx` (App Router) or in `_document.tsx` (Pages Router).
- Keep theme-toggle behavior: it should write to localStorage and update the `<html>` class.
- Measurements vary between runs; focus on removing every identified source, not on a single number.
