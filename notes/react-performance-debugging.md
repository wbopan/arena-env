**Goal:** find and fix the root causes of slowness in a Next.js e-commerce app. The three areas are API routes (waterfalls and blocking work), bundle size (heavy imports on the compare page), and excessive re-rendering (cart add re-renders every ProductCard).

**Hard constraints:**
- Never change or remove any `data-testid` attribute, or any component that carries one.
- Keep every `performance.mark()` call in ProductCard.
- The homepage must still show product data.
- Add-to-cart must still work.
- The compare page "advanced" tab must still render `data-testid="advanced-content"`.

**Step 1 — Inspect cheaply (do not cat whole files):**
- `cd` to the app dir. Run `ls` and `cat package.json | head -40` to note the Next/React versions and heavy dependencies (lodash, moment, chart libs, mathjs, etc.).
- List source files: `find . -path ./node_modules -prune -o \( -name '*.ts*' -o -name '*.js' \) -print | grep -v .next`
- Find suspects: `grep -rn "await\|setTimeout\|import .* from\|useState\|useEffect\|useContext\|performance.mark\|data-testid" app src components lib --include=*.ts* | head -80`
- View individual files with `sed -n '1,80p' file`, so only the relevant parts are printed.

**Step 2 — API routes (`app/api/**/route.ts` or `pages/api`):**
- **Sequential awaits.** Independent `await`s should run in parallel: `const [a,b,c] = await Promise.all([fa(), fb(), fc()])`.
- **Partial dependencies.** Start promises early and await late:
  ```ts
  const p1 = auth(); const p2 = fetchConfig();
  const s = await p1;
  const [cfg, data] = await Promise.all([p2, fetchData(s.id)]);
  ```
- **Defer await until needed.** Move awaits into the branch that actually uses the result, and return early before expensive calls.
- **Blocking side effects.** Logging, analytics or artificial delays before the response should be moved off the critical path. Use `import { after } from 'next/server'` (Next 15+) with `after(() => logX())`. On older versions, fire-and-forget with `void logX().catch(()=>{})`.
- **Caching.** Check the cache before fetching, never fetch and then check. A module-level `Map` or LRU works for cross-request caching. Use `React.cache()` for per-request dedupe in server components.
- **Response shape.** Keep it unchanged, so the homepage still gets the fields it reads.
- **Simulated latency.** If a fake DB uses `setTimeout` delays, don't break its data. Parallelize calls to it and avoid redundant calls instead.

**Step 3 — Bundle size (compare page):**
- **Heavy library in the advanced tab.** Lazy-load it so it only loads when the tab opens:
  ```ts
  import dynamic from 'next/dynamic'
  const Advanced = dynamic(() => import('./AdvancedPanel'), { ssr:false, loading:()=>null })
  ```
  The `data-testid="advanced-content"` must stay in the rendered output once the tab is active.
- **Barrel imports.** `import _ from 'lodash'` or `{x} from 'lodash'` becomes `import x from 'lodash/x'`. For icons, use direct paths. Alternatively set `experimental: { optimizePackageImports: ['lucide-react','lodash', ...] }` in next.config.
- **Heavy work on load.** Replace heavy libraries used for trivial work (moment, full lodash) with native JS where it's simple. Gate heavy computations behind the tab, or wrap them in `useMemo`.
- **Hoisting.** Move big static data and RegExps to module scope.

**Step 4 — Re-renders (cart/homepage):**
- **Context.** Memoize the provider value with `useMemo(() => ({items, addToCart}), [items, addToCart])`. Consider splitting state and actions into two contexts, so ProductCards that only need `addToCart` don't re-render.
- **Stable callbacks.** Use `useCallback` with a functional update, so `addToCart` never changes identity:
  ```ts
  setItems(curr => [...curr, p])
  ```
- **Memoized cards.** Wrap ProductCard: `export default memo(ProductCard)`. Pass primitive or stable props, not freshly created objects or inline arrow functions per render.
- **Lists and derived values.** Lift expensive list filtering/sorting into `useMemo` with narrow dependencies.
- **Lazy initial state.** Use `useState(() => JSON.parse(localStorage...))` when reading from localStorage.
- **Effects.** Remove `useEffect`s that copy props to state or trigger render loops. Narrow deps to primitives (`[user.id]`, not `[user]`).
- **Lookups.** Replace `.find` inside loops with a `Map`.
- **Long lists.** Optionally add CSS `content-visibility:auto; contain-intrinsic-size:0 300px` to cards.
- **Keep the marks.** Leave `performance.mark(...)` lines in ProductCard exactly as they are. Memo reduces how often they fire, which is the point.

**Step 5 — Build and verify:**
1. `npm run build 2>&1 | tail -30`. This catches type and compile errors and shows per-route First Load JS; the compare page should shrink.
2. Start the app with `npm start &` (or `npm run dev &`), then `sleep 5`.
3. Time and spot-check the API:
   ```bash
   curl -s -o /dev/null -w '%{time_total}\n' localhost:3000/api/products
   curl -s localhost:3000/api/products | head -c 300
   ```
   Check the other API routes the same way.
4. Check the homepage renders products: `curl -s localhost:3000 | grep -c 'data-testid'`.
5. Run the measurement script from the browser-testing skill: `npx ts-node <skilldir>/measure.ts http://localhost:3000` and `.../compare`. Look for:
   - parallel rather than sequential request waterfalls
   - totalMs under 1000
   - LayoutCount under 50
   - ScriptDuration under 0.5s
6. Re-grep to confirm `data-testid` count and `performance.mark` are unchanged versus the original: `git diff --stat` and `git diff | grep -E '^-.*(data-testid|performance.mark)'`. That grep must print nothing.
7. Kill the server when done.

**Pitfalls:**
- `next/dynamic` with `ssr:false` must sit in a `'use client'` file for app router.
- Don't change API URL paths or JSON keys.
- Don't delete components that have testids.
- `after()` requires Next ≥15; check the version first.
