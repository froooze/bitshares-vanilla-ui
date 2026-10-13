/* convert_locale_meta_v2.js — rewrite ONE locale dict's `_meta` to the v2
 * provenance shape, in place, touching no other byte of the file.
 *
 * WHY THIS IS A FILE AND NOT A `node -e`. (1) AGENTS.md rule 3: useful scripts
 * live under tooling/, never inline. (2) The rewrite has to be PROVABLE
 * value-neutral, and a one-liner that re-serialises the whole object with
 * JSON.stringify cannot promise that — it would re-escape every non-ASCII
 * character in every Spanish/Chinese/Japanese string. This tool splices the
 * new `_meta` block into the original TEXT and then re-parses the result and
 * compares every non-`_meta` entry against the original, byte for byte,
 * refusing to write when anything else moved. (3) The remaining v1 locales
 * need the same conversion, so the rule must exist once, not per invocation.
 *
 * The high_risk list is ENUMERATED FROM THE RULE, never hand-typed: it is read
 * out of vanilla/js/i18n/risk-keys.js, the same module ConfirmDialog, RiskText,
 * the honesty chip and every test read, so this file cannot hold a stale copy
 * of a rule that moved. Re-typing it by hand is exactly the rot the module
 * exists to prevent.
 *
 * The v1 `translated` list is deliberately NOT carried into v2. It is
 * recomputable exactly — `{k : value(locale,k) !== value(en,k)}` is the same
 * set, because v1's own rule required a listed key to differ from English —
 * and tooling/i18n_translation_census.py prints it, its size and a payload
 * hash. Copying it forward would keep a second, unverifiable copy of a fact
 * the two files already state, under a name that means something different in
 * each shape (`i18n.js`'s allowlisted() reads `coverage` on v2 and
 * `translated` on v1, so one field name with two meanings is the ambiguity v2
 * was written to remove).
 *
 * Usage: node tooling/convert_locale_meta_v2.js <code>   e.g. ... es
 *   Prints: coverage/verified/high_risk counts, the payload hash before and
 *   after, and "values unchanged: yes|no".
 *
 * Never throws for a missing code — it reports and exits 1. Writes only the
 * one named locale file. Created by: building-vanilla-slices skill,
 * i18n-machine-translation plan, task 8.
 */
"use strict";
var assert = require("assert");
var crypto = require("crypto");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
var LOCALES = path.join(ROOT, "vanilla", "locales");
var CODE_RE = /^[A-Za-z][\w-]*$/;

/* flatten: nested locale dict -> {"dotted.key": leaf}, skipping `_meta`.
 * Same rule as tooling/check_i18n.py's flatten(); re-spelling it here would be
 * the one thing that could make coverage disagree with the gate. Params: d
 * object, p optional prefix string. Returns: a flat object. */
function flatten(d, p) {
  var out = {}, k, v;
  p = p || "";
  for (k in d) {
    if (!Object.prototype.hasOwnProperty.call(d, k)) continue;
    if (k === "_meta") continue;
    v = d[k];
    if (v && typeof v === "object") Object.assign(out, flatten(v, p + k + "."));
    else out[p + k] = v;
  }
  return out;
}

/* payloadHash: sha256 of a flattened locale payload, order-free and
 * character-exact. Params: flat object. Returns: hex digest. */
function payloadHash(flat) {
  var keys = Object.keys(flat).sort();
  var canon = keys.map(function (k) { return JSON.stringify([k, flat[k]]); }).join("\n");
  return crypto.createHash("sha256").update(canon, "utf8").digest("hex");
}

/* metaSpan: character span [start, end) of the top-level "_meta" object in a
 * locale file's text. Params: text (whole file). Returns: {start, end} where
 * start indexes the opening brace and end indexes just past the closing brace.
 * Finds the span by brace counting that skips JSON strings, so a "}" inside a
 * Spanish value cannot end the object early. Throws when `_meta` is absent —
 * a dict without one has no shape to preserve or convert. */
function metaSpan(text) {
  var key = text.indexOf('"_meta"');
  if (key === -1) throw new Error('no "_meta" key in file');
  var open = text.indexOf("{", key);
  var depth = 0, i = open, inStr = false, esc = false;
  for (; i < text.length; i++) {
    var c = text[i];
    if (inStr) {
      if (esc) esc = false;
      else if (c === "\\") esc = true;
      else if (c === '"') inStr = false;
      continue;
    }
    if (c === '"') { inStr = true; continue; }
    if (c === "{") depth++;
    else if (c === "}") {
      depth--;
      if (depth === 0) return { start: open, end: i + 1 };
    }
  }
  throw new Error('unterminated "_meta" object');
}

/* renderMeta: a v2 `_meta` object as the text that goes into the file — the
 * top-level value indented by two spaces, matching the surrounding nesting, so
 * the spliced file keeps the indent=2 shape the locale files were written in.
 * Params: meta object. Returns: string (no trailing newline). */
function renderMeta(meta) {
  return JSON.stringify(meta, null, 2).split("\n").join("\n  ");
}

function main(argv) {
  var code = argv[0];
  if (!code || !CODE_RE.test(code)) {
    process.stderr.write("usage: node tooling/convert_locale_meta_v2.js <code>\n");
    return 2;
  }
  var sandbox = {};
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/i18n/risk-keys.js"), "utf8"), sandbox);
  var RiskKeys = sandbox.RiskKeys;
  if (!RiskKeys || typeof RiskKeys.listFor !== "function") {
    process.stderr.write("FAIL: risk-keys.js did not expose RiskKeys.listFor\n");
    return 1;
  }

  var file = path.join(LOCALES, code + ".json");
  var text;
  try {
    text = fs.readFileSync(file, "utf8");
  } catch (e) {
    process.stderr.write("FAIL: " + file + " unreadable: " + e.message + "\n");
    return 1;
  }
  var enFlat = flatten(JSON.parse(fs.readFileSync(path.join(LOCALES, "en.json"), "utf8")));
  var before = JSON.parse(text);
  var flatBefore = flatten(before);
  var oldMeta = (before._meta && typeof before._meta === "object") ? before._meta : {};

  /* `provenance` is preserved only when the file already declares a legal one:
   * only a human may set "human", and a v1 dict has no such field, so this
   * writes "machine" — which is the honest direction to fail in, because it
   * lights the honesty chip instead of hiding a review. `verified` and
   * `high_risk` are hand-curated claims this tool has no authority to invent,
   * so they are preserved; the high_risk list below is re-derived from the rule
   * when the file does not already carry one. */
  var provenance = oldMeta.provenance;
  if (provenance !== "machine" && provenance !== "human") provenance = "machine";
  var meta = {
    version: 2,
    provenance: provenance,
    coverage: Object.keys(flatBefore).sort(),
    verified: Array.isArray(oldMeta.verified) ? oldMeta.verified.slice().sort() : [],
    high_risk: Array.isArray(oldMeta.high_risk)
      ? oldMeta.high_risk.slice().sort()
      : RiskKeys.listFor(flatBefore, enFlat)
  };

  /* coverage is derived from the dict's OWN keys, never manufactured from
   * en.json: a dict that is missing keys cannot be given a coverage claim. */
  var missingFromEn = Object.keys(enFlat).filter(function (k) {
    return !Object.prototype.hasOwnProperty.call(flatBefore, k);
  });
  if (missingFromEn.length) {
    process.stderr.write("FAIL: " + code + ".json is missing " + missingFromEn.length +
      " en key(s) (" + missingFromEn.slice(0, 5).join(", ") + "); a dict with holes " +
      "cannot claim coverage — fill them first\n");
    return 1;
  }

  var span = metaSpan(text);
  var prefix = text.slice(0, span.start);
  var suffix = text.slice(span.end);
  var next = prefix + renderMeta(meta) + suffix;

  /* The proof this tool exists for: every character outside the spliced span
   * must survive, and every non-`_meta` value must survive the re-parse. The
   * two text halves are compared by digest rather than by content, so a failure
   * prints a hash instead of the whole locale file. Either check failing aborts
   * before any write, so a rejected conversion leaves the file untouched. */
  var digest = function (s) {
    return crypto.createHash("sha256").update(s, "utf8").digest("hex");
  };
  var after = JSON.parse(next);
  var flatAfter = flatten(after);
  assert.strictEqual(digest(next.slice(0, prefix.length)), digest(prefix),
    "text before _meta changed");
  assert.strictEqual(digest(next.slice(next.length - suffix.length)), digest(suffix),
    "text after _meta changed");
  assert.deepStrictEqual(flatAfter, flatBefore, "a non-_meta value changed");
  assert.strictEqual(payloadHash(flatAfter), payloadHash(flatBefore), "payload hash moved");

  if (process.argv.indexOf("--check") !== -1) {
    console.log("CHECK OK: " + code + ".json would convert " +
      "(coverage " + meta.coverage.length + ", high_risk " + meta.high_risk.length +
      ", verified " + meta.verified.length + "); nothing written.");
    return 0;
  }
  fs.writeFileSync(file, next, "utf8");

  console.log("converted " + code + ".json: _meta v" + oldMeta.version + " -> v2" +
    (Array.isArray(oldMeta.translated)
      ? " (v1 translated list of " + oldMeta.translated.length + " keys dropped: recomputable)" : ""));
  console.log("  provenance " + meta.provenance + "; verified " + meta.verified.length +
    "; coverage " + meta.coverage.length + "; high_risk " + meta.high_risk.length +
    " (enumerated by RiskKeys.listFor)");
  console.log("  keys whose value differs from en (the v1 translated set): " +
    Object.keys(flatAfter).filter(function (k) { return flatAfter[k] !== enFlat[k]; }).length);
  console.log("  values unchanged: yes; payload sha256 " + payloadHash(flatBefore) +
    " -> " + payloadHash(flatAfter));
  return 0;
}

if (require.main === module) process.exit(main(process.argv.slice(2)));
module.exports = { flatten: flatten, payloadHash: payloadHash, metaSpan: metaSpan };