#!/usr/bin/env node
/* xrate vectors — cross-rate table data core (pure, no DOM, no chain).
 * Hand-computed fixtures prove: direction normalization, 1/2/3-hop BigInt
 * products, unpriced-leg reasons, BFS hop cap + determinism, ranking,
 * column rules, hash round-trip. Exit 0 green, 1 red. */
"use strict";
const XRate = require("/workspace/vanilla/js/api/xrate.js");
const Format = require("/workspace/vanilla/js/api/format.js");

let pass = 0, fail = 0;
function eq(got, want, name) {
  if (JSON.stringify(got) === JSON.stringify(want)) pass++;
  else { fail++; console.log("FAIL " + name + "\n  got  " + JSON.stringify(got) + "\n  want " + JSON.stringify(want)); }
}
function ok(cond, name) { if (cond) pass++; else { fail++; console.log("FAIL " + name); } }

/* Fixture graph (precisions: BTS p5, USD p4, CNY p4, BTC p8):
 *   P1 BTS/USD: last swap paid 100000 BTS (1.0) received 250000 USD (25.0)
 *   P2 USD/CNY: last swap paid 10000 USD (1.0) received 72000 CNY (7.2)
 *   P3 USD/BTC: last swap paid 250000 USD (25.0) received 12500 BTC (0.00012500)
 *   P4 CNY/JPY: no swaps on record (unpriced leg) */
const P1 = { id: "1.19.1", a: "1.3.0", b: "1.3.113" };
const P2 = { id: "1.19.2", a: "1.3.113", b: "1.3.121" };
const P3 = { id: "1.19.3", a: "1.3.113", b: "1.3.861" };
const P4 = { id: "1.19.4", a: "1.3.121", b: "1.3.22" };
const SWAPS = {
  "1.19.1": { paidRaw: "100000", paidId: "1.3.0", paidPrec: 5, recvRaw: "250000", recvId: "1.3.113", recvPrec: 4 },
  "1.19.2": { paidRaw: "10000", paidId: "1.3.113", paidPrec: 4, recvRaw: "72000", recvId: "1.3.121", recvPrec: 4 },
  "1.19.3": { paidRaw: "250000", paidId: "1.3.113", paidPrec: 4, recvRaw: "12500", recvId: "1.3.861", recvPrec: 8 }
};

/* ---- leg fractions: direction-normalized exact rationals ---- */
eq(XRate.legFraction({ pool: "1.19.1", from: "1.3.0", to: "1.3.113", swap: SWAPS["1.19.1"] }),
  { num: "250000", den: "100000", pPaid: 5, pRecv: 4 },
  "1-hop leg BTS->USD keeps raw ratio + precisions");
eq(XRate.legFraction({ pool: "1.19.1", from: "1.3.113", to: "1.3.0", swap: SWAPS["1.19.1"] }),
  { num: "100000", den: "250000", pPaid: 4, pRecv: 5 },
  "reverse leg inverts paid/received, precisions follow the money");
eq(XRate.legFraction({ pool: "1.19.4", from: "1.3.121", to: "1.3.22", swap: null }), null,
  "pool with no swap is unpriced (null, never guessed)");
eq(XRate.legFraction({ pool: "1.19.1", from: "1.3.0", to: "1.3.113",
  swap: { paidRaw: "100000", paidId: "1.3.0", paidPrec: null, recvRaw: "1", recvId: "1.3.113", recvPrec: 4 } }), null,
  "null precision is unpriced, never assumed");
eq(XRate.legFraction({ pool: "1.19.1", from: "1.3.0", to: "1.3.113",
  swap: { paidRaw: "0", paidId: "1.3.0", paidPrec: 5, recvRaw: "1", recvId: "1.3.113", recvPrec: 4 } }), null,
  "zero paid amount is unpriced (no division by zero)");

/* ---- path products: exact BigInt assembly (value = num/den, folded) ---- */
eq(XRate.pathFraction([
    { pool: "1.19.1", from: "1.3.0", to: "1.3.113", swap: SWAPS["1.19.1"] },
    { pool: "1.19.2", from: "1.3.113", to: "1.3.121", swap: SWAPS["1.19.2"] }
  ]), { num: "18000000000000000000", den: "100000000000000000" },
  "2-hop product BTS->USD->CNY assembles raw (25 * 7.2 = 180)");
eq(XRate.pathFraction([
    { pool: "1.19.1", from: "1.3.0", to: "1.3.113", swap: SWAPS["1.19.1"] },
    { pool: "1.19.3", from: "1.3.113", to: "1.3.861", swap: SWAPS["1.19.3"] }
  ]), { num: "3125000000000000000", den: "25000000000000000000000" },
  "2-hop tiny-rate product assembles raw (25 * 0.000005 = 0.000125)");
eq(XRate.pathFraction([
    { pool: "1.19.4", from: "1.3.121", to: "1.3.22", swap: null }
  ]), null, "a path through an unpriced leg is unpriced");

/* ---- end-to-end human strings through the shipped formatter ---- */
function human(frac) {
  var places = XRate.placesFor(frac.num, frac.den);
  return Format.priceSig(Format.formatPrice(frac.num, 0, frac.den, 0, places));
}
eq(human(XRate.pathFraction([
  { pool: "1.19.1", from: "1.3.0", to: "1.3.113", swap: SWAPS["1.19.1"] }])), "25.00",
  "BTS->USD renders 25.00");
eq(human(XRate.pathFraction([
  { pool: "1.19.1", from: "1.3.0", to: "1.3.113", swap: SWAPS["1.19.1"] },
  { pool: "1.19.2", from: "1.3.113", to: "1.3.121", swap: SWAPS["1.19.2"] }])), "180.0",
  "BTS->CNY renders 180.0");
eq(human(XRate.pathFraction([
  { pool: "1.19.1", from: "1.3.0", to: "1.3.113", swap: SWAPS["1.19.1"] },
  { pool: "1.19.3", from: "1.3.113", to: "1.3.861", swap: SWAPS["1.19.3"] }])), "0.0001250",
  "BTS->BTC renders 0.0001250");

/* ---- graph + BFS: hop cap, determinism ---- */
var G = XRate.buildGraph([P1, P2, P3, P4,
  { id: "1.19.5", a: "1.3.22", b: "1.3.999" }]);
var B = XRate.bfs(G, "1.3.0", 3);
eq(B.depth["1.3.0"], 0, "BTS is depth 0");
eq(B.depth["1.3.113"], 1, "USD is 1 hop");
eq(B.depth["1.3.121"], 2, "CNY is 2 hops");
eq(B.depth["1.3.22"], 3, "JPY is 3 hops");
eq(B.depth["1.3.999"], undefined, "4-hop asset is out of scope");
eq(XRate.routeTo(G, B, "1.3.121").map(function (l) { return l.pool; }), ["1.19.1", "1.19.2"],
  "route to CNY runs P1 then P2");
eq(XRate.routeTo(G, B, "1.3.999"), null, "out-of-scope asset has no route");

/* ---- ranking: hops, then newest swap, then symbol ---- */
eq(XRate.rankRows([
    { id: "1.3.121", sym: "CNY", hops: 2, newest: "2026-10-01T00:00:00" },
    { id: "1.3.113", sym: "USD", hops: 1, newest: "2026-09-01T00:00:00" },
    { id: "1.3.861", sym: "BTC", hops: 2, newest: "2026-10-09T00:00:00" }
  ]).map(function (r) { return r.sym; }), ["USD", "BTC", "CNY"],
  "fewer hops first, then newest swap");
eq(XRate.topRows([1, 2, 3], 40).length, 3, "topRows keeps short lists whole");

/* ---- columns: BTS pinned, unknown dropped, hash round-trip ---- */
eq(XRate.normalizeColumns(["USD", "CNY", "USD", "NOPE"], { USD: 1, CNY: 1 }),
  ["BTS", "USD", "CNY"], "BTS first, deduped, unknown dropped");
eq(XRate.normalizeColumns([], {}), ["BTS"], "empty input is BTS alone");
var h = XRate.hashFor(["USD", "CNY"]);
ok(h.indexOf("cols=USD%2CCNY") !== -1 || h.indexOf("cols=USD,CNY") !== -1, "hash carries columns (" + h + ")");
eq(XRate.parseColumns(h), ["USD", "CNY"], "hash parses back (BTS implied)");
eq(XRate.parseColumns("#/cross-rates"), [], "bare hash is empty columns");

console.log("xrate: " + pass + " pass, " + fail + " fail");
process.exitCode = fail ? 1 : 0;
