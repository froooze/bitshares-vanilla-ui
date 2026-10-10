#!/usr/bin/env node
/* Regression vector — Market.deepen must forward the caller's candle count
 * (and the progressive-paint callback) to MarketCandles.deepen.
 *
 * DEFECT (2026-10-10, exchange desk HONEST.USD_BTS "no way to load more
 * data"): the public Market.deepen wrapper (vanilla/js/api/market.js) declared
 * only (baseId, quoteId, bucketSec) and forwarded exactly those three args.
 * The desk (market-desk-panels.deepenOnce) calls Market.deepen(b, q, bucket,
 * count, onPage) with the LIVE count input, but the wrapper silently dropped
 * `count` and `onPage`. Consequences, both observed live on HONEST.USD_BTS:
 *
 *   1. MarketCandles.deepen received countSec=undefined -> fell back to its
 *      2000 default, so the ES window was ALWAYS span(2000 candles). Raising
 *      the count input never widened the ES backfill -> "can't load more".
 *   2. It cached _deepCache under key "...|<bucket>|2000", but candles(count)
 *      merges only when _deepCache.key === "...|<bucket>|<count>". Any count
 *      other than 2000 therefore never merged -> the note read "chain-only".
 *
 * The pool desk calls PoolHistory/swapsToCandles directly (no wrapper), which
 * is why pools were unaffected — this pins the exchange wrapper only.
 *
 * Offline: MarketCandles.deepen is stubbed; no network, no chain.
 */
"use strict";

/* Stub MarketCandles before requiring market.js so the wrapper delegates into
 * a recorder instead of the real backfill. market.js reads the global. */
let recorded = null;
globalThis.MarketCandles = {
  deepen: function (baseId, quoteId, bucketSec, countSec, onPage) {
    recorded = { baseId, quoteId, bucketSec, countSec, onPage };
    return Promise.resolve(null);
  },
  candles: function () { return Promise.resolve({ buckets: [], closes: [] }); },
  timeframes: function () { return Promise.resolve([3600]); },
  vwap: function () { return { human: null, per: [] }; },
  mergeWindows: function () { return []; }
};
/* market.js may reference other globals at load; stub the ones it touches. */
globalThis.Chain = { db: () => Promise.reject(new Error("no chain")), history: () => Promise.reject(new Error("no chain")), call: () => Promise.reject(new Error("no chain")), hasHistory: () => false };
globalThis.Account = { myAccountId: () => Promise.reject(new Error("locked")), myOrders: () => Promise.reject(new Error("locked")) };

const Market = require("/workspace/vanilla/js/api/market.js");

let pass = 0, fail = 0;
function ok(cond, name, extra) {
  if (cond) pass++;
  else { fail++; console.log("FAIL " + name + (extra !== undefined ? "\n  " + extra : "")); }
}

(async function run() {
  // Case A: the exchange desk's exact call shape — count 5000, onPage callback.
  const onPage = function () {};
  await Market.deepen("1.3.0", "1.3.5649", 3600, 5000, onPage);
  ok(!!recorded, "deepen reached MarketCandles");
  ok(recorded.countSec === 5000, "countSec forwarded (want 5000, got " + JSON.stringify(recorded.countSec) + ")");
  ok(recorded.onPage === onPage, "onPage forwarded (want same fn, got " + (recorded.onPage === onPage) + ")");

  // Case B: a different count, to prove it is not hardcoded to one value.
  await Market.deepen("1.3.0", "1.3.5649", 86400, 137);
  ok(recorded.countSec === 137, "countSec forwarded for 137 (got " + JSON.stringify(recorded.countSec) + ")");
  ok(recorded.bucketSec === 86400, "bucketSec forwarded (got " + JSON.stringify(recorded.bucketSec) + ")");

  console.log((fail ? "FAILURES: " + fail : "all pass") + " (" + pass + " pass, " + fail + " fail)");
  process.exitCode = fail ? 1 : 0;
})();