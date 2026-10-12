/* i18n-glossary-test: docs/i18n-glossary/es.md is the artifact an external
 * auditor reads BEFORE trusting a translation, so it must actually cover the
 * vocabulary that goes wrong — not merely exist. Coverage, structure and the
 * one-term-per-concept rule are all checked mechanically, because a glossary
 * that silently loses a row is worse than none: an auditor reads it as
 * complete.
 *
 * The brief's draft only substring-searched the whole file, which a passing
 * mention in prose satisfies (and which a row written for a DIFFERENT concept
 * also satisfies). Here every required term must be a real TABLE ROW, matched
 * on the English cell exactly, so a term cannot be "covered" by accident.
 *
 * Runs: node tooling/i18n-glossary-test.js (exit 0 = green). */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");

var ROOT = path.join(__dirname, "..");
var FILE = path.join(ROOT, "docs/i18n-glossary/es.md");

/* The BitShares term list an auditor must be able to check. The first group
 * is the plan's REQUIRED list; the second is the account/asset/market nouns
 * the article and the signing rows also carry. */
var REQUIRED = [
  "brainkey", "witness", "committee", "worker", "proxy", "vesting", "HTLC",
  "swap", "slate", "liquidity pool", "credit offer", "ticket", "proposal",
  "precision", "orderbook", "limit order", "fee",
  "account", "asset", "smartcoin", "collateral", "balance", "share",
  "market", "block", "transaction"
];

var glossary = fs.readFileSync(FILE, "utf8");

/* --- structure: one markdown table, three columns, every cell filled ----- */
function cells(line) {
  var s = line.trim();
  if (s.charAt(0) !== "|" || s.charAt(s.length - 1) !== "|") return null;
  return s.slice(1, -1).split("|").map(function (c) { return c.trim(); });
}
var rows = [];
glossary.split(/\r?\n/).forEach(function (line) {
  var c = cells(line);
  if (!c || c.length !== 3) return;
  if (/^-+$/.test(c[0].replace(/\s/g, ""))) return;      /* |---|---|---| */
  rows.push(c);
});
assert.ok(rows.length > REQUIRED.length, "glossary has a header row plus every required term");
var header = rows.shift();
assert.deepStrictEqual(header.map(function (h) { return h.toLowerCase(); }),
  ["english term", "spanish term", "note"],
  "the table names its three columns (English | Spanish | note)");

/* --- coverage: every required term is a ROW, not a passing mention ------- */
var byEnglish = {};
rows.forEach(function (r) {
  var en = r[0].toLowerCase();
  assert.ok(!byEnglish[en], "one row per English term, no duplicate: " + en);
  byEnglish[en] = r;
});
var missing = REQUIRED.filter(function (t) { return !byEnglish[t.toLowerCase()]; });
assert.deepStrictEqual(missing, [],
  "glossary covers every BitShares term (missing: " + missing.join(", ") + ")");

/* --- honesty of the columns: a term with no Spanish or no note is a stub -- */
rows.forEach(function (r) {
  assert.ok(r[1].length > 0, "Spanish term present for “" + r[0] + "”");
  assert.ok(r[2].length > 0, "note present for “" + r[0] + "” (why this wording)");
});

/* --- one Spanish term per concept: no synonym split ----------------------- */
var seen = {};
rows.forEach(function (r) {
  var es = r[1].toLowerCase();
  assert.ok(!seen[es], "“" + es + "” maps to one English term only (also: " + seen[es] + ")");
  seen[es] = r[0];
});

/* --- the glossary is about THIS project's languages ------------------------ */
assert.ok(/^#\s/m.test(glossary), "the file has a markdown heading");
assert.ok(glossary.indexOf("i18n-glossary") !== -1 || glossary.indexOf("Spanish") !== -1,
  "the file says what language it governs");

/* --- a citation is evidence, so check it against es.json -----------------
 * Every `key` a note cites must exist in the shipped Spanish dictionary, and
 * — unless the note marks it a counter-example — its value must actually carry
 * the agreed Spanish word. An auditor who checks a citation and finds nothing
 * stops trusting the whole table, so a truncated or invented key fails here
 * rather than in the reader's face. (Checking the Spanish term's FIRST word,
 * plural-tolerant, keeps inflections from reading as drift: "Pools de
 * liquidez" proves "pool de liquidez" just as well.) */
var esDict = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/es.json"), "utf8"));
function esFlat(dict, prefix) {
  var out = {};
  prefix = prefix || "";
  Object.keys(dict).forEach(function (k) {
    if (k === "_meta") return;
    if (dict[k] && typeof dict[k] === "object") Object.assign(out, esFlat(dict[k], prefix + k + "."));
    else out[prefix + k] = dict[k];
  });
  return out;
}
var esValues = esFlat(esDict);
/* head word of the Spanish term, plural-tolerant: "Pools de liquidez" is
 * evidence for "pool de liquidez", so a trailing s must not read as drift. */
function headWord(term) {
  var head = String(term).split(" ")[0].toLowerCase();
  return head.length > 4 && head.charAt(head.length - 1) === "s" ? head.slice(0, -1) : head;
}
var citations = [];
rows.forEach(function (r) {
  var re = /`([a-z][A-Za-z0-9_.]*)`/g, m;
  /* A "counter-example" marker exempts only the citations that FOLLOW it, so
   * a note can still prove its own term with the key it opens with. */
  var counterAt = r[2].search(/counter-example/i);
  while ((m = re.exec(r[2])) !== null) {
    citations.push({ term: r[0], esTerm: r[1], key: m[1],
      isCounter: counterAt !== -1 && m.index > counterAt });
  }
});
assert.ok(citations.length >= 20, "the notes cite real keys as evidence (" + citations.length + " citations)");
var badKey = [], badProof = [];
citations.forEach(function (c) {
  var value = esValues[c.key];
  if (typeof value !== "string") { badKey.push(c.term + " -> " + c.key); return; }
  if (c.isCounter) return;                               /* cited to disagree, on purpose */
  if (String(value).toLowerCase().indexOf(headWord(c.esTerm)) === -1) {
    badProof.push(c.term + " -> " + c.key);
  }
});
assert.deepStrictEqual(badKey, [], "every cited key exists in es.json");
assert.deepStrictEqual(badProof, [], "every evidence citation really shows the agreed Spanish word");

console.log("OK: i18n-glossary (" + REQUIRED.length + " required terms, " +
  rows.length + " rows, " + citations.length + " citations verified)");
