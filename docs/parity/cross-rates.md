# Parity Note — Cross Rates (`#/cross-rates`)

Date: 2026-10-12. Slice: new read-only page (spec
`docs/superpowers/specs/2026-10-12-cross-rates-design.md`, plan
`docs/superpowers/plans/2026-10-12-cross-rates.md`).
Data-only: reads pool list + per-pool swap history + asset symbols; no
transaction is ever built, signed, or broadcast here.

## 1. Reference behavior

- **#1 `bitshares-ui`:** no cross-rate table exists anywhere in the
  reference wallet (verified: no `cross-rate`/`crossrate` string in
  `reference/bitshares-ui/app`). Closest analogs are per-pair pool
  desks; the matrix itself is owner-specified new behavior.
- **#2 `astro-ui`:** no equivalent found (same grep, `src/`).
- **Crypo template `cross-rates-dark/light.html`:** NOT a table — a
  remote TradingView forex-widget iframe. No DOM to port and must not
  be depended on. Appearance reverse-engineered by screenshot
  measurement only (evidence kept outside the repo:
  `/tmp/opencode/tv-cross-*.png`): black `#000000` ground,
  `#2f2f2f` hairlines, white right-aligned ~13px numerals,
  `#242424` diagonal, `#7e1c24`/`#03341b` day-change tints,
  `#0e2157` hover crosshair (cell + row/column headers), ~53px
  rows, sticky first column + horizontal scroll at 390px width.
- **Chain contract (#4 wins):** `list_liquidity_pools(limit?,
  start_id?, with_statistics=false)` —
  `database_api.hpp:701` (paginate from `start_id`, trailing
  optionals omittable); `get_liquidity_pool_history(pool_id, start?,
  stop?, limit?, operation_type?)` newest-first —
  `api.hpp:266` (op codes 59–63 listed inline, 63 = exchange).
  `Pool.list`/`Pool.history` already wrap both (ambiguity probes +
  history-api-with-db-fallback intact, untouched by this slice).

## 2. Vanilla implementation

| File | Lines | Owns |
|---|---|---|
| `vanilla/js/api/xrate.js` | ~210 | pure matrix core: BFS ≤3 from BTS, direction-normalized leg fractions, exact BigInt multi-hop products, ranking, column rules, `?cols=` contract |
| `vanilla/js/views/xrate-ui.js` | ~540 | page shell, pool walk, route-only swap fetching (~8-wide batches, progressive paint), table, picker/chips, click-through, hash sync, connect gate |
| `vanilla/css/app.css` | +28 | `.xrate-*` block (scroll region, sticky header, tabular numerals, diagonal, hover, chips, phone opt-out) |
| `vanilla/css/themes.css` | +3 tokens ×3 | `--xrate-diag`, `--xrate-hot`, `--xrate-hot-text` (measured values dark/light, rhymed ref) |
| `vanilla/js/router.js`, `menu-ui.js`, `index.html`, `globals.d.ts` | — | route + SEO meta, Trade link, script tags, type decls |
| `vanilla/locales/*.json` | 12 | 22 new keys per locale (3917 total) via `tooling/add_xrate_i18n.py` |
| `tooling/xrate-test.js` | 25 vectors | hand-computed fixtures (see §4) |
| `tooling/visual/probe-xrate.mjs` | — | behavioral + visual gate (kept) |

Deliberate deviations from the measured widget (all honest, all
recorded): untinted cells (widget tints by day-change, a signal we do
not have — inventing one would be fabrication); flag icons replaced by
symbol text (no per-asset icon set exists); gridlines reuse `--border`
(#2a2e39 vs measured #2f2f2f: 5-step deviation, imperceptible,
token-clean); header cell keeps the "Asset" label (widget corner is
empty; screen readers need the label). Numbers right-align was
measurement-overruled (eyeball said centered; text-mass centroid
proved right-aligned).

## 3. Manual test steps + observed result

Mainnet (live, reads only), `tooling/visual/probe-xrate.mjs`:
`#/cross-rates` → h1 "Cross Rates", 40 rows,
"515 pools · 172 assets within 3 hops · 161 of 171 pools hold a last
swap"; first cell links `#/pools/1.19.59`; click lands on the pool
desk; diagonal marked; theme trio × desktop + 360px phone all render
with no overflow; zero console errors.

Testnet (testnet.xbts.io): 20 pools, 10 in-scope assets, "6 of 9 pools
hold a last swap" — priced cells (`CONTEST.BTC 0.004730`,
`SWAPBTS 2.210`) alongside honest "—" cells (`CNY`,
`NBLU7901220`, `XRPBTS` — routes through swap-less pools); zero
errors. Small chain exercises both paths in one shot.

Click-through: cell → `#/pools/<first pool from the row asset>`,
route in title; row header → `#/asset/<symbol>`; `?cols=USD,CNY`
round-trips; invalid tokens rejected with reason; BTS column pinned.

## 4. Raw → human test vectors (#6)

All 25 vectors in `tooling/xrate-test.js` pin literals (no Format in
core — core returns exact `{num, den}` rationals; the view formats):

| Raw | Rule | Display | Vector |
|---|---|---|---|
| P1 swap paid `100000`@BTS(p5) → recv `250000`@USD(p4) | leg fraction, direction-normalized | `25.00` | 1-hop BTS→USD |
| + P2 paid `10000`@USD(p4) → recv `72000`@CNY(p4) | product `(25/1)·(7.2/1)` in raw space | `180.0` | 2-hop BTS→CNY |
| + P3 paid `250000`@USD(p4) → recv `12500`@BTC(p8) | product `25·0.000005` | `0.0001250` | tiny-rate 2-hop |
| P1 reversed (paid USD, recv BTS) | paid/recv invert with precisions | same `25.00` | direction guard |
| pool with no swap / null precision / zero paid / endpoint mismatch | null, never guessed | "—" + reason | unpriced legs |
| 4-hop asset in fixture graph | BFS cap | excluded, no route | hop cap |
| `?cols=` unknown/dupes | BTS-first, dedupe, drop unknown | `[BTS,USD,CNY]` | column rules |

`placesFor` derives format decimals from digit lengths (pure integer
magnitude); `Format.formatPrice` rounds half-up; `priceSig` renders
the global 4-sig rule (`1.577e-8` observed live). No `Math.pow(10,
precision)` anywhere outside `format.js`; no binary float touches
money (ranking uses hop counts, ISO-time strings, and symbol order).

## 5. Themes, viewports, a11y

- `xrate-{ref,dex-ux,vanilla-ui}-desk.png` + `xrate-dex-phone.png`
  (`/tmp/opencode/`, probe-generated per run).
- Cells link to pools (native anchors: mouse + touch + keyboard +
  screen-reader free); row headers link to asset pages; token input
  has label + datalist; status line is `aria-live`; table via
  `TableRenderer` (`th scope`, sticky first col inherent).
- 44px touch floor on buttons/chips via shared `touchable`; no
  hover-only UI (hover crosshair is enhancement-only; taps never need
  it); phone keeps the table via the `.xrate-scroll` opt-out with
  horizontal scroll + sticky first column (the widget's own 390px
  behavior, verified in-shot).
- One observed-once anomaly, unreproduced in 3 follow-up runs
  (enumerated every anchor color live: all accent): a single phone
  screenshot showed one lime row. Treated as a compositor tear during
  progressive repaint, recorded here; reopen if ever seen again.

## 6. Readability (§3.7)

Module headers state owns/consumes/globals/created-by; every
non-trivial function has what/params/returns/failure JSDoc; comments
explain WHY (provenance, honesty rules, measured values); no
TODO/FIXME (grepped); shared `DOM`/`Forms`/`TableRenderer`/`touchable`
used, no local copies; no dead CSS (scan count back at baseline 19);
no dead files committed (one-off `dbg-*`/`shot-*` probes deleted,
`probe-xrate.mjs` kept).

## 7. Anti-rot gate (§4.5)

- (a) Ten years, nothing updated: static files + two proven chain
  calls; worst case the page shows its honest offline state. The
  measured styling is hand-written CSS from pixels — no
  TradingView code, dependency, or asset copied.
- (b) New dependencies: **none**. New trust: none (same node, same
  `Pool.list` + `get_liquidity_pool_history` the pool desks already
  use).
- (c) Smallest deletable subset: view + route + menu link; the `xrate.js`
  core stays useful to pool desks later (kept: single-purpose, tested).

## 8. Gates

- `xrate-test` **25/25** · `menu-test` **28** · `check_types.sh` PASS ·
  `check_i18n.py` OK (3917 keys, 5129 call sites) · `check_rot.py`
  PASSED · `scan_dead_css` baseline 19 (zero added) ·
  `probe-xrate.mjs` PASS (matrix, links, click-through, trio, phone,
  zero console errors).
