# Cross-Rates Table — Implementation Plan

Date: 2026-10-12. Spec: `docs/superpowers/specs/2026-10-12-cross-rates-design.md`.
Slice size: one read-only page; verifiable in one session (mainnet reads
for live data, testnet for render/empty/offline states).

## 1. Files

CREATE:
- `vanilla/js/api/xrate.js` — pure matrix core: BFS ≤3 from BTS over
  pool edges; route records `{pools[], legs[{pool, from, to, paidRaw,
  paidPrec, recvRaw, recvPrec, time, block}]}`; BigInt cross-rate
  assembly via `Format.formatPrice` + `priceSig`; top-40 rank (hops,
  newest route-swap, symbol); per-cell `{text|reason, route[], poolId}`
  records. Zero DOM, zero chain — fully unit-testable. (~250 lines)
- `vanilla/js/views/xrate-ui.js` — page shell: `DOM.pageHead` h1,
  explainer, token input + datalist, column chips (remove buttons),
  status line, `TableRenderer` table, `Event.delegate` cell clicks,
  refresh, show-all expander, `?cols=` hash sync, gen-guarded teardown.
  (~330 lines)
- `tooling/xrate-test.js` — pure vectors: hand-computed 1/2/3-hop rates
  across mixed precisions, direction normalization, unpriced-leg
  reasons, BFS hop cap, ranking determinism, column add/remove/persist
  rules, hash round-trip. (~150 lines)

MODIFY:
- `vanilla/js/router.js` — route `{ path: "/cross-rates", ... }` +
  `ROUTE_META` entry (title ≤60ch, desc ≤155ch).
- `vanilla/js/views/menu-ui.js` — Trade link (`menu.p_xrates` keys);
  update `tooling/menu-test.js` counts (53→54 pages, trade 8→9).
- `vanilla/index.html` — script tags (`xrate.js`, `xrate-ui.js`,
  `?v=` token, dependency order).
- `vanilla/js/globals.d.ts` — `XRate`, `XRateUI` declarations.
- `vanilla/css/app.css` — append `.xrate-*` block (scroll region,
  sticky header + first col, right-aligned tabular-nums cells,
  diagonal/dash/hover states, chips, input; tokens only + TV tint
  literals with provenance comments).
- `vanilla/locales/*.json` (12) — `xrate.*` + `menu.p_xrates` keys via
  existing `add_*_i18n.py` pattern (new script
  `tooling/add_xrate_i18n.py`), English-verified, rest honest stubs.
- `tooling/visual/viewport-audit.mjs` — add `#/cross-rates` route.
- `docs/parity/cross-rates.md` — 8-field parity note (new).

## 2. Build order

1. **Data core first** (`xrate.js` + `xrate-test.js`, TDD): fixtures are
   hand-built pool graphs with known swaps; assert exact human strings
   (proves precision handling, direction, multi-hop products).
2. **Wire reads**: `Pool.list` pagination → BFS → rank → batched
   `lookup_asset_symbols` → parallel `chainSwaps(poolId, 10)` for route
   pools only → progressive paint. Reuse, don't reimplement.
3. **View**: shell → table → picker/chips → clicks → hash → refresh →
   expander → empty/offline states. Every string keyed from the first
   render (no hardcoded-text retrofit).
4. **CSS**: `.xrate-*` against the measured TV spec; verify trio +
   phone/desktop via probe, fix, re-shoot.
5. **Route/menu/meta/i18n/viewport-audit** wiring; update menu-test.
6. **Parity note** with test vectors (raw swap legs → displayed cell),
   theme trio + viewport screenshots, gates evidence.

## 3. Test & gates

- `node tooling/xrate-test.js` (new, must be green first).
- Regression: pool-ui/graph/history suites touching reused paths.
- `bash tooling/check_types.sh`, `python3 tooling/check_i18n.py`,
  `tooling/check_rot.py`, `tooling/scan_dead_css.py` (new block),
  `node tooling/menu-test.js`.
- Probe `tooling/visual/probe-xrate.mjs` (saved, per rule 3): theme
  trio × phone/desktop screenshots, click-through target assertion
  (`#/pools/<first-hop-id>`), zero console errors.
- Live matrix on mainnet (reads only); testnet pass covers render,
  empty-scope, and offline states.

## 4. Risks & answers

- **N pools × history calls**: mitigated by route-only fetching +
  ~8-wide batches + progressive paint (spec §4).
- **Testnet pool scarcity**: expected; parity records mainnet-live +
  testnet-states explicitly (read-only page, no signing to prove).
- **Anti-rot (a)** 2036-test: static files + vendored nothing new; worst
  case the table shows honest offline state. **(b)** New deps: none; new
  trust: none (same node + same two proven calls). **(c)** Smallest
  deletable subset: view + route + menu link; core stays useful to
  pool desks later (kept: single-purpose, tested).
