/* i18n-v2-meta-test: the i18n gates must enforce the three-state `_meta`
 * version 2 model — `provenance` (machine-filled vs human-reviewed),
 * `coverage` ("this dict has a value for every key"), `verified` (the keys a
 * human signed off) and `high_risk` (the dual-line signing strings) — and must
 * keep the OLD lie fatal.
 *
 * WHY THIS EXISTS. v1 conflated two different claims in one field:
 * `_meta.translated` said both "this dict has a value for every key" (a
 * COVERAGE claim) and "a human translated these" (a TRUST claim). Nothing
 * could check the second one, so 8,098 false translation claims accumulated in
 * silence. v2 separates them, which means the gates must learn a second,
 * stricter shape without forgetting the first — and that is exactly the kind
 * of "two code paths that must agree" change that rots if only one of them is
 * tested.
 *
 * WHAT IS PROVEN HERE (every case is a mutation of a well-formed dict, so
 * each fails without the gate rule it exercises):
 *   1. a well-formed v2 dict passes BOTH gates;
 *   2. so does the `provenance:"human"` form with a non-empty `verified` —
 *      the model must stay satisfiable, not just strict;
 *   3. a `verified` key whose value equals en is rejected (both gates): a
 *      human signed it off, so an English value means the CLAIM is wrong;
 *   4. `coverage` drift (an extra key and a missing key) is rejected;
 *   5. `high_risk` naming a key that does not exist is rejected;
 *   6. `provenance:"human"` with an empty `verified` is rejected — it is the
 *      cheapest possible way to silence the "machine translated" warning, so
 *      it has to be fatal, not advisory;
 *   7. a `provenance` outside {machine, human} is rejected;
 *   8. a `verified` key outside `coverage` is rejected;
 *   9. a `verified` key whose value MUST equal en by design (identifier,
 *      network/theme id, brand) is rejected: check 4 of
 *      validate_translations demands byte-verbatim equality there, so
 *      "verified implies different" and "must be identical" would otherwise
 *      deadlock and make a legitimately reviewed dict unfalsifiable;
 *  10. IDENTICAL-TO-en values that are NOT verified are NOT fatal for a v2
 *      dict — they are reported as a counted review note. This is the
 *      deliberate change from v1: a machine string may legitimately coincide
 *      with English (loanwords: DEX, HTLC, URL), and a gate cannot tell a
 *      loanword from a machine that copied English. It can only queue the
 *      question for a human. Case 11 below pins the asymmetry that this
 *      creates against the v1 path, which still refuses it;
 *  11. THE OLD LIE IS STILL FATAL: a v1 dict that CLAIMS a key whose value
 *      equals English is rejected by both gates;
 *  12. `--fix-meta` on a v2 dict preserves the v2 shape (and does not
 *      manufacture a `verified` claim it cannot know);
 *  13. `--fix-meta` on a v1 dict still writes the v1 shape.
 *
 * ISOLATION. The real working tree is never mutated: each case copies
 * tooling/{check_i18n,validate_translations}.py + vanilla/{index.html,js,
 * locales} into a fresh temp directory (the checker resolves its own ROOT from
 * its own __file__, exactly as in production), swaps the temporary dict in as
 * that copy's es.json, and restores the original bytes in a `finally` before
 * deleting the copy. The shipped es.json is additionally byte-compared to a
 * snapshot taken at startup, so a gate test can never leave the repo's locale
 * corrupted — not even on an assertion failure, and not even for the other
 * agents working in this tree at the same time.
 */
"use strict";
var assert = require("assert");
var fs = require("fs");
var os = require("os");
var path = require("path");
var cp = require("child_process");

var ROOT = path.join(__dirname, "..");
var REAL_ES = path.join(ROOT, "vanilla", "locales", "es.json");
var ES_AT_START = fs.readFileSync(REAL_ES);
/* --verbose prints what each gate actually SAID, per case. The crafted dicts
 * live in this file and nowhere else, so this is how the rejection rules are
 * demonstrated on real data without a second copy of them to drift. */
var VERBOSE = process.argv.indexOf("--verbose") !== -1;

var passed = 0;
function ok(cond, msg) {
  assert.ok(cond, msg);
  passed += 1;
  if (VERBOSE) console.log("  ok  " + msg.split(" — ")[0]);
}

/* ---- the English master ------------------------------------------------- */

var enDict = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla", "locales", "en.json"), "utf8"));

/* leafKeys: the dotted leaf paths of a dict, minus _meta — the same flatten
 * rule both Python gates use (a list is a leaf, not a branch). */
function leafKeys(d, prefix) {
  var out = [];
  prefix = prefix || "";
  Object.keys(d).forEach(function (k) {
    if (k === "_meta") return;
    var v = d[k];
    if (v !== null && typeof v === "object" && !Array.isArray(v)) {
      out = out.concat(leafKeys(v, prefix + k + "."));
    } else {
      out.push(prefix + k);
    }
  });
  return out.sort();
}
var EN_KEYS = leafKeys(enDict, "");

function getPath(obj, key) {
  var node = obj, parts = key.split(".");
  for (var i = 0; i < parts.length; i++) {
    if (node === null || typeof node !== "object") return undefined;
    node = node[parts[i]];
  }
  return node;
}
function setPath(obj, key, value) {
  var parts = key.split("."), node = obj;
  for (var i = 0; i < parts.length - 1; i++) {
    if (!node[parts[i]] || typeof node[parts[i]] !== "object") node[parts[i]] = {};
    node = node[parts[i]];
  }
  node[parts[parts.length - 1]] = value;
}

/* Keys chosen for their PROOF OBLIGATION, not for convenience:
 *  K_TRANSLATED — a real, translatable key; the dict carries a DIFFERENT value,
 *                  so it can legally sit in `verified`;
 *  K_PLAIN      — a real key the dict leaves equal to English, so claiming it
 *                  verified is provably a false claim;
 *  K_IDENT      — `shell.brand`, whose value both gates REQUIRE to equal en
 *                  byte-for-byte (identifier preservation). */
var K_TRANSLATED = "menu.p_dashboard";
var K_PLAIN = "menu.p_transfer";
var K_IDENT = "shell.brand";
var TRANSLATED_VALUE = "Tablero de control";

ok(getPath(enDict, K_TRANSLATED) === "Dashboard", "K_TRANSLATED is a real, translatable en key");
ok(getPath(enDict, K_PLAIN) === "Transfer", "K_PLAIN is a real en key the dict may leave alone");
ok(getPath(enDict, K_IDENT) === "BitShares", "K_IDENT is a real identifier key");
ok(K_TRANSLATED !== K_PLAIN && K_PLAIN !== K_IDENT, "the proof keys are distinct");

/* baseValues: every en key present, carrying en's own value EXCEPT
 * K_TRANSLATED. So a dict built on top is honest under v1 rules (nothing
 * unclaimed differs from en) and exercises every v2 rule at once. */
function baseValues() {
  var d = {};
  EN_KEYS.forEach(function (k) { setPath(d, k, getPath(enDict, k)); });
  setPath(d, K_TRANSLATED, TRANSLATED_VALUE);
  return d;
}

function v2(over) {
  var d = baseValues();
  d._meta = {
    version: 2,
    provenance: "machine",
    coverage: EN_KEYS.slice(),
    verified: [],
    high_risk: [K_TRANSLATED]
  };
  if (over) over(d._meta, d);
  return d;
}

/* v1Lie: claims K_PLAIN as translated while its value is still English —
 * the 8,098-claim rot, in miniature. Every other key is an honest stub, so
 * the ONLY thing wrong with this dict is the claim. */
function v1Lie() {
  var d = baseValues();
  setPath(d, K_TRANSLATED, getPath(enDict, K_TRANSLATED));   /* nothing else translated */
  d._meta = { version: 1, untranslated: false, translated: [K_PLAIN] };
  return d;
}

/* ---- sandbox ------------------------------------------------------------ */

function copyTree(src, dst) {
  var st = fs.statSync(src);
  if (st.isDirectory()) {
    fs.mkdirSync(dst, { recursive: true });
    fs.readdirSync(src).forEach(function (name) { copyTree(path.join(src, name), path.join(dst, name)); });
    return;
  }
  fs.copyFileSync(src, dst);
}

var seq = 0;
function sandbox() {
  var dir = fs.mkdtempSync(path.join(os.tmpdir(), "i18n-v2-" + (seq++) + "-"));
  fs.mkdirSync(path.join(dir, "tooling"), { recursive: true });
  fs.mkdirSync(path.join(dir, "vanilla"), { recursive: true });
  ["check_i18n.py", "validate_translations.py"].forEach(function (f) {
    fs.copyFileSync(path.join(ROOT, "tooling", f), path.join(dir, "tooling", f));
  });
  copyTree(path.join(ROOT, "vanilla", "js"), path.join(dir, "vanilla", "js"));
  copyTree(path.join(ROOT, "vanilla", "locales"), path.join(dir, "vanilla", "locales"));
  fs.copyFileSync(path.join(ROOT, "vanilla", "index.html"), path.join(dir, "vanilla", "index.html"));
  return dir;
}

function py(dir, script, args) {
  var r = cp.spawnSync("python3", [path.join(dir, "tooling", script)].concat(args), { encoding: "utf8" });
  return { code: r.status, out: (r.stdout || "") + (r.stderr || "") };
}
function check(dir) { return py(dir, "check_i18n.py", []); }
function validate(dir) { return py(dir, "validate_translations.py", ["es"]); }
function headLines(out, n) { return out.split("\n").filter(Boolean).slice(0, n).join(" | "); }

/* withEs: build a sandbox, swap in a temporary dict as its es.json, run body,
 * and restore the original bytes in a `finally` — a thrown assertion still
 * restores. The sandbox is then deleted; the real tree was never written. */
function withEs(makeDict, body) {
  var dir = sandbox();
  var esPath = path.join(dir, "vanilla", "locales", "es.json");
  var original = fs.readFileSync(esPath);
  try {
    fs.writeFileSync(esPath, JSON.stringify(makeDict(), null, 2) + "\n");
    body(dir, esPath);
  } finally {
    fs.writeFileSync(esPath, original);
    try { fs.rmSync(dir, { recursive: true, force: true }); } catch (e) { /* tmp is disposable */ }
  }
}

function expectPass(dir, label) {
  var c = check(dir), v = validate(dir);
  ok(c.code === 0, label + ": check_i18n.py passes — " + headLines(c.out, 2));
  ok(v.code === 0, label + ": validate_translations.py passes — " + headLines(v.out, 2));
  if (VERBOSE) {
    console.log("--- " + label + ": check_i18n.py (exit " + c.code + ") ---");
    console.log(c.out.trim());
    console.log("--- " + label + ": validate_translations.py (exit " + v.code + ") ---");
    console.log(v.out.trim());
  }
}

function expectFail(dir, label, needle) {
  var c = check(dir), v = validate(dir);
  ok(c.code === 1, label + ": check_i18n.py rejects (exit " + c.code + ") — " + headLines(c.out, 2));
  ok(v.code === 1, label + ": validate_translations.py rejects (exit " + v.code + ") — " + headLines(v.out, 2));
  ok(c.out.indexOf(needle) !== -1,
    label + ": check_i18n names the problem (" + needle + ") — " + headLines(c.out, 3));
  ok(v.out.indexOf(needle) !== -1,
    label + ": validate_translations names the problem (" + needle + ") — " + headLines(v.out, 3));
  if (VERBOSE) {
    console.log("--- " + label + ": check_i18n.py (exit " + c.code + ") ---");
    console.log(c.out.trim());
    console.log("--- " + label + ": validate_translations.py (exit " + v.code + ") ---");
    console.log(v.out.trim());
  }
}

/* ---- 1. a well-formed v2 dict passes both gates ------------------------- */
withEs(function () { return v2(); }, function (dir) {
  expectPass(dir, "well-formed machine v2 dict");
});

/* ---- 2. the human form is satisfiable too ------------------------------- */
/* A gate that only ever says NO is not a gate. `verified` non-empty +
 * provenance "human" + every verified value differing from en must pass. */
withEs(function () {
  return v2(function (m) { m.provenance = "human"; m.verified = [K_TRANSLATED]; });
}, function (dir) {
  expectPass(dir, "human-reviewed v2 dict with a genuinely translated key");
});

/* ---- 3. verified, but the value is still English ------------------------ */
withEs(function () {
  return v2(function (m) { m.verified = [K_PLAIN]; });
}, function (dir) {
  expectFail(dir, "verified key whose value equals en", "identical to en");
});

/* ---- 4. coverage drift, both directions --------------------------------- */
withEs(function () {
  return v2(function (m) {
    m.coverage = m.coverage.slice(1);              /* missing one key */
    m.coverage.push("no.such.key");                /* …and one extra   */
  });
}, function (dir) {
  expectFail(dir, "coverage drift (extra and missing)", "coverage");
});

/* ---- 5. high_risk naming a key that does not exist ---------------------- */
withEs(function () {
  return v2(function (m) { m.high_risk = [K_TRANSLATED, "no.such.key"]; });
}, function (dir) {
  expectFail(dir, "high_risk with an unknown key", "high_risk");
});

/* ---- 6. "human" that signed off nothing --------------------------------- */
withEs(function () {
  return v2(function (m) { m.provenance = "human"; m.verified = []; });
}, function (dir) {
  expectFail(dir, "provenance human with empty verified", "provenance");
});

/* ---- 7. a provenance outside the two legal values ----------------------- */
withEs(function () {
  return v2(function (m) { m.provenance = "machien"; });
}, function (dir) {
  expectFail(dir, "unknown provenance value", "provenance");
});

/* ---- 8. verified outside coverage --------------------------------------- */
withEs(function () {
  return v2(function (m) { m.verified = [K_TRANSLATED, "no.such.key"]; });
}, function (dir) {
  expectFail(dir, "verified key outside coverage", "verified");
});

/* ---- 9. verified a key that MUST equal English by design --------------- */
/* Without this rule the model is self-defeating: validate_translations check 4
 * REQUIRES identifiers byte-verbatim, while "verified implies different" would
 * forbid the same key from ever being reviewed. The resolution is the one v1
 * already used: an identifier is not a translation, so it is not claimable. */
withEs(function () {
  return v2(function (m) { m.provenance = "human"; m.verified = [K_TRANSLATED, K_IDENT]; });
}, function (dir) {
  expectFail(dir, "verified an identifier whose value must equal en", K_IDENT);
});

/* ---- 10/11. the deliberate asymmetry ----------------------------------- */
/* The SAME dict content is legal under v2 (values that merely coincide with
 * English are a review queue, not a failure) and illegal under v1 (where the
 * identical value is a claim the gate can actually refute). Both halves are
 * pinned, because "simplify the gate by rejecting everything identical to en"
 * is the exact regression that would make every machine-filled locale
 * unfalsifiable. */
withEs(function () { return v2(); }, function (dir) {
  expectPass(dir, "machine v2 dict whose values coincide with en");
  var out = check(dir).out;
  var m = out.match(/(\d+) machine value\(s\) equal en/);
  ok(m !== null && Number(m[1]) > 0,
    "and the coincidence is reported as a COUNTED review note, not a failure — " +
    out.split("\n").filter(function (l) { return l.indexOf("machine value") !== -1; }).join(""));
});

withEs(function () { return v1Lie(); }, function (dir) {
  expectFail(dir, "v1 dict CLAIMING an English-identical key", K_PLAIN);
});

/* ---- 12. --fix-meta preserves v2 ---------------------------------------- */
withEs(function () {
  return v2(function (m) { m.provenance = "human"; m.verified = [K_TRANSLATED]; m.high_risk = [K_TRANSLATED]; });
}, function (dir, esPath) {
  var fixed = py(dir, "validate_translations.py", ["--fix-meta", "es"]);
  ok(fixed.code === 0, "--fix-meta succeeds — " + headLines(fixed.out, 2));
  var meta = JSON.parse(fs.readFileSync(esPath, "utf8"))._meta;
  ok(meta.version === 2, "--fix-meta does not DEMOTE a v2 dict to v1 (got version " + meta.version + ")");
  ok(meta.provenance === "human", "--fix-meta preserves provenance (got " + JSON.stringify(meta.provenance) + ")");
  ok(Array.isArray(meta.verified) && meta.verified.length === 1 && meta.verified[0] === K_TRANSLATED,
    "--fix-meta preserves the human's verified list verbatim (got " + JSON.stringify(meta.verified) + ")");
  ok(Array.isArray(meta.high_risk) && meta.high_risk.length === 1 && meta.high_risk[0] === K_TRANSLATED,
    "--fix-meta preserves high_risk (got " + JSON.stringify(meta.high_risk) + ")");
  ok(Array.isArray(meta.coverage) && meta.coverage.length === EN_KEYS.length,
    "--fix-meta recomputes coverage from the dict's own keys (got " +
    (Array.isArray(meta.coverage) ? meta.coverage.length : typeof meta.coverage) + ")");
  ok(meta.untranslated === undefined && meta.translated === undefined,
    "--fix-meta writes no v1 fields onto a v2 dict (got " + JSON.stringify(Object.keys(meta)) + ")");
  var again = validate(dir);
  ok(again.code === 0, "and the rewritten dict still validates — " + headLines(again.out, 2));
});

/* ---- 13. --fix-meta on a v1 dict still writes v1 ------------------------ */
withEs(function () {
  var real = JSON.parse(fs.readFileSync(REAL_ES, "utf8"));
  real._meta.translated = real._meta.translated.slice(0, 10);   /* a stale list */
  return real;
}, function (dir, esPath) {
  var before = JSON.parse(fs.readFileSync(esPath, "utf8"))._meta;
  var fixed = py(dir, "validate_translations.py", ["--fix-meta", "es"]);
  ok(fixed.code === 0, "--fix-meta succeeds on a v1 dict — " + headLines(fixed.out, 2));
  var meta = JSON.parse(fs.readFileSync(esPath, "utf8"))._meta;
  ok(meta.version === 1, "--fix-meta keeps the v1 shape (got version " + meta.version + ")");
  ok(meta.untranslated === false, "--fix-meta keeps untranslated:false");
  ok(meta.translated.length > before.translated.length,
    "--fix-meta rebuilds the v1 allowlist from the dict (" + before.translated.length +
    " -> " + meta.translated.length + ")");
  ok(meta.provenance === undefined, "and writes no v2 fields onto a v1 dict");
});

/* ---- the real tree survived -------------------------------------------- */
ok(fs.readFileSync(REAL_ES).equals(ES_AT_START),
  "the repo's es.json is byte-identical after the run — a gate test must never "
  + "leave a locale corrupted");

console.log("i18n _meta v2 gate: " + passed + " passed, 0 failed");
