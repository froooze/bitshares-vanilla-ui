/* xrate.js — cross-rate table data core (pure, no DOM, no chain).
 * Owns: pool-graph topology + BFS route finding (BTS outward, hop-capped),
 *   direction-normalized per-leg rate fractions from last-swap paid/received
 *   legs, exact BigInt multi-hop products, row ranking, column rules, and
 *   the ?cols= hash contract. Amounts stay raw digit strings here; the view
 *   renders through Format.formatPrice + priceSig (never binary float).
 * Consumes: nothing (all inputs are plain caller-built objects).
 * Side effects: none. Global XRate (declared in globals.d.ts for tsc).
 * Created by: cross-rates slice, spec
 *   docs/superpowers/specs/2026-10-12-cross-rates-design.md.
 */
var XRate = (function () {
  "use strict";

  /* BTS core id: consensus literal (1.3.0 on mainnet AND testnet contract
   * here — the page's base column; a chain without BTS at 1.3.0 simply
   * yields an empty scope, honestly). */
  var BTS_ID = "1.3.0";
  /* Depth + display caps (owner-confirmed): 3 hops, top 40 + expander. */
  var MAX_DEPTH = 3;
  var TOP_N = 40;

  /**
   * isId: strict 1.3.x asset id reader.
   * @param {*} v Raw value.
   * @returns {boolean} True for a canonical asset id.
   */
  function isId(v) {
    return /^1\.3\.\d+$/.test(String(v === undefined || v === null ? "" : v));
  }

  /**
   * isDigits: strict unsigned integer string reader (raw chain amounts).
   * @param {*} v Raw value.
   * @returns {boolean} True for digits only (empty rejected).
   */
  function isDigits(v) {
    return typeof v === "string" && /^[0-9]+$/.test(v);
  }

  /**
   * isPrec: precision reader (per-asset decimal places, 0..12).
   * @param {*} v Raw value.
   * @returns {boolean} True for an integer precision.
   */
  function isPrec(v) {
    return typeof v === "number" && isFinite(v) &&
      Math.floor(v) === v && v >= 0 && v <= 12;
  }

  /**
   * buildGraph: pool rows -> adjacency (undirected: swaps run either way).
   * @param {Array<{id:string,a:string,b:string}>} pools Pool edge list.
   * @returns {{adj:Object<string,Array<{pool:string,other:string}>>,poolsById:Object}} Graph.
   * Failure: never throws — malformed rows are skipped, never guessed.
   */
  function buildGraph(pools) {
    var adj = {}, poolsById = {};
    (pools || []).forEach(function (p) {
      if (!p || !(/^1\.19\.\d+$/.test(String(p.id))) || !isId(p.a) || !isId(p.b) || p.a === p.b) return;
      poolsById[p.id] = { id: p.id, a: p.a, b: p.b };
      if (!adj[p.a]) adj[p.a] = [];
      if (!adj[p.b]) adj[p.b] = [];
      adj[p.a].push({ pool: p.id, other: p.b });
      adj[p.b].push({ pool: p.id, other: p.a });
    });
    return { adj: adj, poolsById: poolsById };
  }

  /**
   * bfs: fewest-hop distances + tree edges from the start asset.
   * @param {Object} graph buildGraph output.
   * @param {string} startId Seed asset id (BTS).
   * @param {number} maxDepth Hop cap.
   * @returns {{depth:Object<string,number>,via:Object<string,{pool:string,from:string}>}} Depths + tree edge per node.
   * Failure: never throws — bad input yields an empty result.
   */
  function bfs(graph, startId, maxDepth) {
    var depth = {}, via = {};
    try {
      if (!graph || !graph.adj || !isId(startId)) return { depth: depth, via: via };
      var cap = (typeof maxDepth === "number" && maxDepth >= 0) ? Math.floor(maxDepth) : MAX_DEPTH;
      var queue = [String(startId)];
      depth[String(startId)] = 0;
      while (queue.length) {
        var cur = queue.shift();
        var d = depth[cur];
        if (d >= cap) continue;
        var edges = graph.adj[cur] || [];
        for (var i = 0; i < edges.length; i++) {
          var nxt = edges[i].other;
          if (depth[nxt] !== undefined) continue;
          depth[nxt] = d + 1;
          via[nxt] = { pool: edges[i].pool, from: cur };
          queue.push(nxt);
        }
      }
    } catch (e) { /* empty result stands */ }
    return { depth: depth, via: via };
  }

  /**
   * routeTo: tree path from the BFS seed to a target (seed-first order).
   * @param {Object} graph buildGraph output (unused today: path reads via only; kept so callers pass one shape).
   * @param {Object} bfsRes bfs output.
   * @param {string} targetId Destination asset id.
   * @returns {Array<{pool:string,from:string,to:string}>|null} Legs seed-first, [] for the seed, null when unreachable.
   */
  function routeTo(graph, bfsRes, targetId) {
    try {
      if (!bfsRes || !bfsRes.depth || bfsRes.depth[targetId] === undefined) return null;
      var legs = [], cur = String(targetId);
      while (bfsRes.depth[cur] > 0) {
        var e = (bfsRes.via || {})[cur];
        if (!e) return null;
        legs.unshift({ pool: e.pool, from: e.from, to: cur });
        cur = e.from;
      }
      return legs;
    } catch (e) { return null; }
  }

  /**
   * legFraction: one directed leg -> exact raw ratio with precision context.
   * A leg X->Y with swap paid P of X @px / received R of Y @py means
   * (R/10^py)/(P/10^px); the reverse direction inverts paid/received.
   * @param {Object} leg {pool, from, to, swap:{paidRaw,paidId,paidPrec,recvRaw,recvId,recvPrec}|null}.
   * @returns {{num:string,den:string,pPaid:number,pRecv:number}|null} Raw ratio + context, or null when unpriced (no swap, null precision, zero/malformed amounts, endpoint mismatch — never guessed, never thrown).
   */
  function legFraction(leg) {
    try {
      if (!leg || !isId(leg.from) || !isId(leg.to)) return null;
      var s = leg.swap;
      if (!s || !isDigits(s.paidRaw) || !isDigits(s.recvRaw)) return null;
      if (!isPrec(s.paidPrec) || !isPrec(s.recvPrec)) return null;
      var paidId = String(s.paidId), recvId = String(s.recvId);
      var from = String(leg.from), to = String(leg.to);
      var num, den, pPaid, pRecv;
      if (paidId === from && recvId === to) {
        num = s.recvRaw; den = s.paidRaw; pPaid = s.paidPrec; pRecv = s.recvPrec;
      } else if (paidId === to && recvId === from) {
        num = s.paidRaw; den = s.recvRaw; pPaid = s.recvPrec; pRecv = s.paidPrec;
      } else {
        return null;
      }
      if (num === "" || den === "") return null;
      var nz = false;
      for (var i = 0; i < den.length; i++) { if (den.charCodeAt(i) !== 48) { nz = true; break; } }
      if (!nz) return null;
      return { num: num, den: den, pPaid: pPaid, pRecv: pRecv };
    } catch (e) { return null; }
  }

  /**
   * pathFraction: multi-hop product folded to ONE exact rational whose
   * value is num/den (precisions folded in: num=Πrecv·Π10^pPaid,
   * den=Πpaid·Π10^pRecv), ready for formatPrice(num,0,den,0,places).
   * @param {Array} legs legFraction-shaped legs (routeTo output + swaps attached by the caller).
   * @returns {{num:string,den:string}|null} Folded exact ratio, or null when empty/any leg unpriced.
   */
  function pathFraction(legs) {
    try {
      if (!legs || !legs.length) return null;
      var num = 1n, den = 1n;
      for (var i = 0; i < legs.length; i++) {
        var f = legFraction(legs[i]);
        if (!f) return null;
        num = num * BigInt(f.num) * (10n ** BigInt(f.pPaid));
        den = den * BigInt(f.den) * (10n ** BigInt(f.pRecv));
      }
      return { num: num.toString(), den: den.toString() };
    } catch (e) { return null; }
  }

  /**
   * placesFor: decimal places that keep 4 significant figures alive through
   * formatPrice (which rounds at `places`). Magnitude from digit lengths —
   * pure integer reasoning, never float.
   * @param {string} num Folded numerator digits.
   * @param {string} den Folded denominator digits.
   * @returns {number} 0..15 (garbage in -> 8, the candle default).
   */
  function placesFor(num, den) {
    try {
      if (!isDigits(num) || !isDigits(den)) return 8;
      var order = num.replace(/^0+/, "").length - den.replace(/^0+/, "").length;
      if (order > 20 || order < -20) return 8;
      var p = 6 - order;
      if (p < 0) return 0;
      if (p > 15) return 15;
      return p;
    } catch (e) { return 8; }
  }

  /**
   * rankRows: fewest hops, then newest route swap, then symbol (determinism
   * is a feature: same chain state always paints the same table).
   * @param {Array<{id:string,sym:string,hops:number,newest:string}>} rows Candidates.
   * @returns {Array} New sorted array (input untouched).
   */
  function rankRows(rows) {
    var out = (rows || []).slice();
    out.sort(function (a, b) {
      if (a.hops !== b.hops) return a.hops - b.hops;
      var na = a.newest || "", nb = b.newest || "";
      if (na !== nb) return na < nb ? 1 : -1;
      var sa = String(a.sym || a.id), sb = String(b.sym || b.id);
      return sa < sb ? -1 : (sa > sb ? 1 : 0);
    });
    return out;
  }

  /**
   * topRows: display cap (owner-confirmed 40 + expander).
   * @param {Array} rows Ranked rows. @param {number} n Cap.
   * @returns {Array} First n (whole list when shorter).
   */
  function topRows(rows, n) {
    var list = rows || [];
    var cap = (typeof n === "number" && n > 0) ? Math.floor(n) : TOP_N;
    return list.slice(0, cap);
  }

  /**
   * normalizeColumns: user token columns -> [BTS, ...known, deduped].
   * BTS is pinned first (the page's base); unknown symbols dropped.
   * @param {Array<string>} input Raw symbols. @param {Object} known {SYM:1} pool-network symbols.
   * @returns {Array<string>} Column symbols.
   */
  function normalizeColumns(input, known) {
    var out = ["BTS"], seen = { BTS: 1 };
    (input || []).forEach(function (s) {
      var sym = String(s === undefined || s === null ? "" : s).trim().toUpperCase();
      if (!sym || seen[sym]) return;
      if (sym !== "BTS" && !(known && known[sym])) return;
      seen[sym] = 1;
      out.push(sym);
    });
    return out;
  }

  /**
   * hashFor: shareable columns -> "#/cross-rates?cols=A,B".
   * @param {Array<string>} columns Column symbols (BTS implied, omitted).
   * @returns {string} Hash target.
   */
  function hashFor(columns) {
    var rest = (columns || []).filter(function (s) { return s && s !== "BTS"; });
    return "#/cross-rates?cols=" + encodeURIComponent(rest.join(","));
  }

  /**
   * parseColumns: hash -> column symbols (BTS implied, never included).
   * Unknown params ignored; malformed hash yields [] (never throws).
   * @param {string} hash location.hash (or any string).
   * @returns {Array<string>} Column symbols in order, deduped.
   */
  function parseColumns(hash) {
    var out = [], seen = {};
    try {
      var s = String(hash === undefined || hash === null ? "" : hash);
      var qi = s.indexOf("?");
      if (qi === -1) return out;
      var parts = s.slice(qi + 1).split("&");
      for (var i = 0; i < parts.length; i++) {
        var eqi = parts[i].indexOf("=");
        if (eqi === -1) continue;
        var k = "", v = "";
        try { k = decodeURIComponent(parts[i].slice(0, eqi)); } catch (e) { k = parts[i].slice(0, eqi); }
        try { v = decodeURIComponent(parts[i].slice(eqi + 1)); } catch (e2) { v = parts[i].slice(eqi + 1); }
        if (k !== "cols") continue;
        v.split(",").forEach(function (x) {
          var sym = String(x || "").trim().toUpperCase();
          if (sym && !seen[sym]) { seen[sym] = 1; out.push(sym); }
        });
      }
    } catch (e) { return []; }
    return out;
  }

  return {
    BTS_ID: BTS_ID, MAX_DEPTH: MAX_DEPTH, TOP_N: TOP_N,
    buildGraph: buildGraph, bfs: bfs, routeTo: routeTo,
    legFraction: legFraction, pathFraction: pathFraction,
    placesFor: placesFor, rankRows: rankRows, topRows: topRows,
    normalizeColumns: normalizeColumns, hashFor: hashFor,
    parseColumns: parseColumns
  };
})();

if (typeof globalThis !== "undefined" && typeof globalThis.XRate === "undefined") { globalThis.XRate = XRate; }
if (typeof module !== "undefined") { module.exports = XRate; }
