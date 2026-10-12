# Cross-Rates Table — Design

Date: 2026-10-12. Status: approved by owner (price source, row scope,
column memory, TV-measured styling, navigation, cell click-through all
confirmed in brainstorm).
Scope: one new read-only page `#/cross-rates` — a currency-matrix table
of BitShares pool prices. No signing, no broadcasts, no state writes
except the URL hash.

## 1. Goal

Give the user the missing question in the wallet: **"what is asset X
worth in BTS (or USD, CNY, …) right now on the pools?"** Today prices
live one pair at a time inside pool detail desks. This page answers it
as a matrix: rows are assets, columns are quote tokens, every cell is a
price crossed through the pool graph at the last executed swap.

## 2. Decisions (from brainstorm, all owner-confirmed)

- **Price source: last executed swap per pool.** Each leg's rate comes
  from the newest `liquidity_pool_exchange` (op 63) row for that pool
  (`paid`/`received` + precisions), via the proven
  `PoolHistory.chainSwaps` path — never the spot balance ratio, never
  fabricated. A leg with no swap on record is unpriced, and any cell
  whose route contains one renders "—" with the reason in its title.
- **Row scope: every asset within 3 pool hops of BTS, top-40 +
  expander.** BFS over the pool graph from BTS (`1.3.0` literal) to
  depth 3; rank hops-asc, then newest route-swap time desc, then symbol
  asc; show 40, disclose the remainder behind a "show all" expander.
- **Columns: BTS pinned + user-added tokens.** One text input lists any
  asset present in the pool network (datalist of joined symbols);
  each added token becomes a removable column chip. BTS cannot be
  removed. Session-only (no localStorage); shareable via
  `?cols=USD,CNY` in the hash.
- **Styling: pixel-measured TradingView replica, hand-built.** The
  Crypo `cross-rates-*` pages are a remote TradingView iframe (no DOM,
  nothing to port, must not depend on). Appearance reverse-engineered
  by screenshot measurement (`/tmp/opencode/tv-cross-*.png`): black
  `#000000` ground, `#2f2f2f` hairlines, white right-aligned tabular
  numbers, `#242424` diagonal, `#7e1c24` / `#03341b` tints,
  `#0e2157` hover crosshair (cell + row/column headers), ~13px type,
  ~53px rows, sticky first column + horizontal scroll on narrow
  screens. Rebuilt with theme tokens (zero new HEX except the
  widget-specific tints, which ship as scoped literals with provenance
  comments citing this measurement).
- **Tint semantics: untinted initially.** The widget tints by
  per-pair day-change, a signal we do not have; inventing one would be
  fabrication. Structure ships tint-ready (cell class hook); coloring
  waits for a real change signal. Explicit, reversible, recorded.
- **Navigation: Trade section menu entry** ("Cross Rates"), route
  `#/cross-rates`, full SEO meta. Reachable with no login.
- **Click-through: any rate cell → its pool.** Target is the FIRST pool
  on the path starting from the row asset (the actionable start of a
  swap journey): `#/pools/<1.19.x>`. The full route (pool ids + per-leg
  swap times) rides in the cell's title. Row headers link to
  `#/asset/<symbol>`.

## 3. Verified chain-index facts

| Fact | Consequence |
|---|---|
| `list_liquidity_pools(limit?, start_id?, with_statistics=false)` — `database_api.hpp:701`; paginate from `start_id`, omit trailing optionals | Pool-graph topology in ~6 calls of 100; `Pool.list` already wraps the 2-arg/3-arg ambiguity |
| `get_liquidity_pool_history(pool_id, start?, stop?, limit?, operation_type?)` — `api.hpp:266`, newest-first; op codes 59–63 listed inline (`63-exchange`) | Newest swap per route pool via `Pool.history(poolId, 10)` + op-63 filter (`PoolHistory.chainSwaps`, proven 2026-09-28; 101-row chain cap respected) |
| Swap result carries `paid{amount, asset_id}` + `received{...}` (`pool-history.js:393-430` extraction, live-proven) | Per-leg rate needs no other field; legs missing either side are shape-skips, counted |
| Pool objects carry `asset_a_id/asset_b_id` + raw balances (`pool.js:104`) | BFS edges + symbol joins free from the list call |
| `lookup_asset_symbols` — `database_api.hpp:444`, batched joins precedent in `credit.js` | One batched symbol/precision join for every id the matrix names |

## 4. Architecture

```
#/cross-rates (Trade menu)
├─ xrate-ui.js (view): pageHead h1, token input + datalist, column chips,
│   status line, TableRenderer table, Event.delegate cell clicks,
│   refresh button, show-all expander, ?cols= hash sync
├─ xrate.js (data, pure): BFS ≤3 from BTS over pool edges; route pick
│   (fewest hops, then newest swap); BigInt cross-rate assembly;
│   top-40 rank; per-cell {value|reason, route[]} records
├─ Pool.list (paged) → topology + balances
├─ PoolHistory.chainSwaps(poolId, 10) → newest op-63 per ROUTE pool only
├─ lookup_asset_symbols (batched) → symbols + precisions
└─ Format.formatPrice (integer-only) + priceSig (4-sig global rule)
```

- **Fetch discipline:** pool list first (cheap, ~6 calls); BFS in memory;
  rank rows; fetch last-swaps ONLY for pools on kept routes, ~8-wide
  parallel batches, progressive table paint, gen-guarded teardown.
  Unkept pools are never queried — the "show all" expander fetches its
  routes on demand the same way.
- **Money discipline (#6):** raw digit strings until render; cross rate
  assembled as `baseRaw=Πrecv·Π10^pPaid, basePrec=0` /
  `quoteRaw=Πpaid·Π10^pRecv, quotePrec=0` through `formatPrice`, then
  `priceSig`. No binary float anywhere; no cross-asset sums (each cell
  is one row asset in one column token by construction).

## 5. Honesty rules (no blank panels, no invented numbers)

- Unpriced leg → cell "—", title names the pool + "no swaps yet".
- Asset beyond 3 hops → never a row (scope is stated above the table).
- Index/node down → the page's standard offline state + retry; partial
  route failures paint what resolved and say what didn't
  ("priced 37/40 routes").
- Every number carries provenance in its title: per-leg swap
  time/block + pool id.
- Statuses count, never adjectives: routes priced, swaps read, legs
  skipped + why.

## 6. Non-goals

Live ticking (manual refresh only — stated on page); order-book markets
(this is pools-only; order-book cross rates are a different data
source); write paths of any kind; a fourth visual language (TV skin
rebuilt strictly inside the three shipped themes).
