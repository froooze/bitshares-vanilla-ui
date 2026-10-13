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
 * The second half is the honesty half, and it exists because the first version
 * of this table shipped the MINORITY word on two rows: `swap → canje` (3
 * strings against 13 that kept the loanword) and `proxy → apoderado` (1
 * against 16). An auditor following either row would have rewritten a dozen
 * correct pool and voting strings — the one job of this file is to prevent
 * that. So each row's Spanish term is counted against the shipped es.json, a
 * row that declares a rejected form must list EVERY string using it, and a row
 * may not forbid a word the shipped dictionaries use more than its own term.
 *
 * Two machine-readable note markers carry that (documented in es.md's "How to
 * use it"):
 *   Counter-example form: `word`  — the form this row REJECTS for its concept.
 *   Same root, other sense:       — citations after it use the word correctly
 *                                   for a DIFFERENT concept, so they are listed
 *                                   for the reader but are neither evidence nor
 *                                   counter-examples.
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
 * — unless the note marks it a counter-example or a same-root other sense —
 * its value must actually carry the agreed Spanish word. An auditor who checks
 * a citation and finds nothing stops trusting the whole table, so a truncated
 * or invented key fails here rather than in the reader's face. (Checking the
 * Spanish term's FIRST word, plural-tolerant, keeps inflections from reading
 * as drift: "Pools de liquidez" proves "pool de liquidez" just as well.) */
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
var enValues = esFlat(JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/en.json"), "utf8")));
/* A stub is a value byte-equal to the English master — an honest unverified
 * copy, which says nothing about the Spanish vocabulary. Only a value that
 * DIFFERS from English is a claim about wording, so only those are counted. */
function isTranslated(key) {
  var v = esValues[key];
  return typeof v === "string" && v !== enValues[key];
}
function translatedKeys() {
  return Object.keys(esValues).filter(isTranslated).sort();
}
var ALL_TRANSLATED = translatedKeys();
/* The rejected-form marker: names a Spanish WORD, so it is lifted out of the
 * note before citation parsing (see below). */
var REJECT_MARKER_RE = /Counter-example form:\s*`[^`]+`/i;
/* uses: translated es.json values whose text contains `word` at a word
 * boundary, inflections included ("canje" finds canje/canjear/canjeador).
 * Word-bounded so "swap" never matches inside a longer Spanish word. */
function uses(word) {
  var re = new RegExp("\\b" + String(word) + "\\w*", "i");
  return ALL_TRANSLATED.filter(function (k) { return re.test(esValues[k]); });
}
/* head word of the Spanish term, plural-tolerant: "Pools de liquidez" is
 * evidence for "pool de liquidez", so a trailing s must not read as drift. */
function headWord(term) {
  var head = String(term).split(" ")[0].toLowerCase();
  return head.length > 4 && head.charAt(head.length - 1) === "s" ? head.slice(0, -1) : head;
}
var citations = [];
rows.forEach(function (r) {
  /* The `Counter-example form: `word`` marker names a WORD, not a key, so it
   * is lifted out before citation parsing — otherwise it reads as a citation of
   * a nonexistent locale key. */
  var note = r[2].replace(REJECT_MARKER_RE, "Counter-example form:");
  /* Hyphens are in the class on purpose: locale keys carry them (help slugs
   * like `help.topic_dex-intro_body`), and a class without one silently failed
   * to capture such a key at all — a citation that was never checked. */
  var re = /`([a-z_][A-Za-z0-9_.-]*)`/g, m;
  /* A marker exempts only the citations that FOLLOW it, so a note can still
   * prove its own term with the key it opens with. */
  var counterAt = note.search(/counter-example|same root, other sense/i);
  while ((m = re.exec(note)) !== null) {
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

/* --- HONESTY: the agreed term is the one es.json actually uses -------------
 * The defect this exists to catch: a row whose Spanish cell names a word the
 * shipped dictionaries mostly do NOT use. Following such a row rewrites correct
 * strings — the auditor is the one most likely to act on it. Two checks:
 *
 *  1. every row reports its term's real count against es.json, so the table's
 *     grounding is visible in the test output, not just in prose;
 *  2. a row that REJECTS a form (`Counter-example form:`) must lose: the
 *     rejected form's count may not exceed the agreed term's, and every
 *     translated string using the rejected form must be named — as a
 *     counter-example or as a same-root other sense. A partial list is the
 *     other half of the bug: it leaves strings the auditor will "fix" wrongly.
 */
var usage = [];
rows.forEach(function (r) {
  var agreed = uses(r[1]);
  usage.push({ term: r[0], es: r[1], count: agreed.length });
});
var REJECT_RE = /Counter-example form:\s*`([^`]+)`/i;
var minority = [], incomplete = [], rejected = [];
rows.forEach(function (r) {
  var m = REJECT_RE.exec(r[2]);
  if (!m) return;
  var alt = m[1];
  var altKeys = uses(alt);
  rejected.push({ term: r[0], alt: alt, agreed: uses(r[1]).length, altCount: altKeys.length });
  if (altKeys.length > uses(r[1]).length) {
    minority.push(r[0] + " mandates “" + r[1] + "” (" + uses(r[1]).length +
      " strings) but rejects “" + alt + "\" (" + altKeys.length + " strings) — the majority form");
  }
  /* Every string using the rejected form must be accounted for: named in the
   * note (either as a counter-example or as a same-root other sense), so an
   * auditor reads all of them rather than a sample. */
  var named = citations.filter(function (c) { return c.term === r[0]; })
    .map(function (c) { return c.key; });
  var unaccounted = altKeys.filter(function (k) { return named.indexOf(k) === -1; });
  if (unaccounted.length) {
    incomplete.push(r[0] + " (“" + alt + "”) unlisted: " + unaccounted.join(", "));
  }
});
assert.deepStrictEqual(minority, [],
  "no row may mandate the minority form for its concept");
assert.deepStrictEqual(incomplete, [],
  "every string using a rejected form is named in its row");
assert.ok(rejected.length >= 2, "at least two rows declare a rejected form (" + rejected.length + ")");

/* --- HONESTY: a row may not forbid the word es.json actually ships ---------
 * A "Never “x”" / "Not “x”" in a note is an instruction. If x appears in more
 * translated strings than the row's own agreed term, the note orders a mass
 * rewrite of correct strings — so it must be rejected here. The escape hatch is
 * real: a word that is ANOTHER row's agreed term (`intercambio` = the exchange
 * venue, forbidden only for the act of swapping) is fine, and so is a word no
 * dictionary ships at all. */
var agreedTerms = {};
rows.forEach(function (r) { agreedTerms[headWord(r[1])] = r[0]; });
var bans = [];
rows.forEach(function (r) {
  var re = /(?:\bNever|\bNot)\s+[“"]([^”"]+)[”"]/gi, m;
  while ((m = re.exec(r[2])) !== null) bans.push({ term: r[0], banned: m[1] });
});
var badBans = [];
bans.forEach(function (b) {
  var n = uses(b.banned).length;
  var own = uses(rows.filter(function (r) { return r[0] === b.term; })[0][1]).length;
  if (n === 0) return;                                   /* ships nowhere: safe */
  if (Object.prototype.hasOwnProperty.call(agreedTerms, headWord(b.banned))) return;  /* another concept's word */
  if (n > own) badBans.push(b.term + " forbids “" + b.banned + "” (" + n + " strings) over its own term (" + own + ")");
});
assert.deepStrictEqual(badBans, [],
  "a note never forbids the form es.json uses more than the row's own term");

console.log("OK: i18n-glossary (" + REQUIRED.length + " required terms, " +
  rows.length + " rows, " + citations.length + " citations verified)");
console.log("  usage of each mandated term in translated es.json strings:");
usage.forEach(function (u) {
  console.log("    " + u.term + " -> " + u.es + ": " + u.count +
    (u.term.length < 22 ? " ".repeat(22 - u.term.length) : " "));
});
rejected.forEach(function (r) {
  console.log("  rejected form " + r.alt + " for “" + r.term + "”: " +
    r.altCount + " string(s) vs " + r.agreed + " for the agreed term — majority form kept");
});
