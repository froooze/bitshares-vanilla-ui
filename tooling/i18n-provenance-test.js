/* i18n-provenance-test: the honesty surfaces all ask the same three
 * questions (is this locale machine-filled, what is the English source,
 * is this key verified). They must answer from the registry, never from
 * a re-read of the file, so all three are pinned here.
 *
 * Three notes on how the shipped code actually behaves, all documented in
 * .superpowers/sdd/task-2-report.md (1-2 are deviations from the task-2
 * brief's draft test; 3 is the review finding this wave fixes):
 *   1. `registry.en` is NOT seeded at init — loadCached() fetches
 *      locales/en.json asynchronously and app.js renders only after it
 *      settles. The brief asserted enFor() synchronously at module load;
 *      that is only reachable by embedding a 389 KB copy of en.json in
 *      i18n.js, so this test pins the real contract instead: undefined
 *      (never a throw) before boot, the real master afterwards — seeded
 *      through the module's own `_seed` test seam, same dict the app
 *      loads from disk.
 *   2. "menu.dashboard" is not a key in en.json (the menu section uses
 *      menu.p_dashboard / menu.d_dashboard). A test must resolve a key
 *      that actually ships, so it uses menu.p_dashboard and byte-checks
 *      the value against en.json.
 *   3. The en master can be ABSENT. loadCached() resolves {ok:true} even
 *      when the en fetch fails (it swallows the error), and app.js boots
 *      on both resolutions, so the whole active locale can render with
 *      registry.en empty. Reproduced against the shipped code: t() then
 *      answers from the call-site default while enFor() returned
 *      undefined — a machine-labeled locale with no English reference,
 *      exactly the dishonesty this whole change exists to prevent. The
 *      default t() is given is therefore recorded and used as enFor's
 *      fallback; the boot scenario is pinned at the bottom of this file. */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
var sandbox = { console: console, fetch: function () { return Promise.reject(new Error("offline")); } };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/i18n.js"), "utf8"), sandbox);
var I18n = sandbox.I18n;

assert.strictEqual(typeof I18n.enFor, "function", "enFor exists");
assert.strictEqual(typeof I18n.provenance, "function", "provenance exists");
assert.strictEqual(typeof I18n.isMachineLocale, "function", "isMachineLocale exists");

/* en is never a machine locale and never needs a warning. */
assert.strictEqual(I18n.provenance("en"), "none");
assert.strictEqual(I18n.isMachineLocale("en"), false);

/* An unloaded or unknown locale reports "none" — never a false warning. */
assert.strictEqual(I18n.provenance("zz"), "none");
assert.strictEqual(I18n.isMachineLocale("zz"), false);

/* Pre-boot (en still loading) enFor is undefined and NEVER throws: the
 * honesty surfaces render during boot too, and a badge must not be able
 * to take the page down over a dictionary that has not landed yet. */
assert.strictEqual(I18n.enFor("menu.p_dashboard"), undefined, "pre-boot enFor is undefined");
assert.strictEqual(I18n.enFor(null), undefined, "enFor tolerates a null key");
assert.strictEqual(I18n.enFor(42), undefined, "enFor tolerates a non-string key");
/* Inherited members are not entries: both the master dict and the
 * recorded-default map are read with hasOwnProperty, so a prototype
 * name can never pose as an English source. */
assert.strictEqual(I18n.enFor("toString"), undefined, "prototype names are not keys");
assert.strictEqual(I18n.enFor("constructor"), undefined, "no constructor key");

/* Seed the REAL English master (the dict loadCached fetches, read
 * Node-side — no network, no second copy of the data in this test).
 * esDict is the real shipped Spanish dict, served by the boot scenario
 * at the bottom of this file. */
var enDict = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/en.json"), "utf8"));
var esDict = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/es.json"), "utf8"));
I18n._seed("en", enDict);

/* enFor resolves against the English master: the whole point is that the
 * reference text is available without a second string at the call site. */
var k = "menu.p_dashboard";
var en = I18n.enFor(k);
assert.strictEqual(typeof en, "string");
assert.ok(en.length > 0, "enFor resolves a real key");
assert.strictEqual(en, enDict.menu.p_dashboard, "enFor is the master, verbatim");

/* Unknown keys stay unknown — strict dotted traversal, no prefix match
 * ("menu" exists, "menu.dashboard" does not). */
assert.strictEqual(I18n.enFor("no.such.key"), undefined);
assert.strictEqual(I18n.enFor("menu.dashboard"), undefined, "no prefix/truthy match");
assert.strictEqual(I18n.enFor("_meta.version"), undefined, "the key itself never leaks _meta");

/* The recorded call-site default is a FALLBACK, never an override: with
 * the master loaded, t() may be handed a default that disagrees with it,
 * and the shipped master must still win — a stale record can never
 * displace the dict every other surface reads. */
I18n.t(k, "SOME STALE DEFAULT");
assert.strictEqual(I18n.enFor(k), enDict.menu.p_dashboard,
  "the master wins over a recorded default");

/* A key the master does not have is answerable from the record alone —
 * this is what keeps the English reference alive when the en fetch
 * failed, and it is bounded by the key space, not by call volume. */
var unseeded = "no.such.key";
assert.strictEqual(I18n.enFor(unseeded), undefined, "unrecorded key stays undefined");
assert.strictEqual(I18n.t(unseeded, "Recorded English"), "Recorded English");
assert.strictEqual(I18n.enFor(unseeded), "Recorded English",
  "a non-empty default is recorded and served as the English reference");

/* Only real strings are recorded: a missing or empty default must leave
 * enFor undefined rather than hand the honesty surfaces a blank English
 * line (a missing reference is better than an empty one). */
assert.strictEqual(I18n.t("empty.default.key", ""), "", "an empty default still renders");
assert.strictEqual(I18n.enFor("empty.default.key"), undefined, "an empty default is not recorded");
assert.strictEqual(I18n.t("missing.default.key"), "missing.default.key",
  "with no default t() returns the key id");
assert.strictEqual(I18n.enFor("missing.default.key"), undefined, "no default is not recorded");
assert.strictEqual(I18n.t("null.default.key", null), "null.default.key",
  "a non-string default is not a source");
assert.strictEqual(I18n.enFor("null.default.key"), undefined, "null is not recorded");

/* Version-aware allowlist, observed through t() (the only caller).
 * v2 dicts are authoritative on _meta.coverage, v1 on _meta.translated —
 * reading the wrong one silently disables the fallback for that dict. */
I18n._seed("v2", { _meta: { version: 2, provenance: "machine", coverage: [k], translated: ["menu.p_transfer"] },
  menu: { p_dashboard: "PANEL", p_transfer: "TRANSFER" } });
I18n._seed("v1", { _meta: { version: 1, untranslated: false, translated: [k], coverage: ["menu.p_transfer"] },
  menu: { p_dashboard: "Panneau", p_transfer: "Transfert" } });

I18n._setCurrent("v2");
assert.strictEqual(I18n.t(k), "PANEL", "v2 reads _meta.coverage");
assert.strictEqual(I18n.t("menu.p_transfer"), enDict.menu.p_transfer, "v2 ignores _meta.translated");

I18n._setCurrent("v1");
assert.strictEqual(I18n.t(k), "Panneau", "v1 reads _meta.translated");
assert.strictEqual(I18n.t("menu.p_transfer"), enDict.menu.p_transfer, "v1 ignores _meta.coverage");

/* A v2 dict whose coverage is MISSING or is not an array claims nothing,
 * so every key falls back to English. The dict's own value must never
 * render on the strength of a broken declaration — a machine fill that
 * cannot prove coverage is exactly the false claim this model replaces.
 * Pinned because "partial coverage" (a real array listing some keys) is
 * the easy case and silently covers neither of these. */
I18n._seed("v2nocov", { _meta: { version: 2, provenance: "machine" },
  menu: { p_dashboard: "PANEL-NO-COV", p_transfer: "TRANSFER-NO-COV" } });
I18n._seed("v2strcov", { _meta: { version: 2, provenance: "machine", coverage: "menu.p_dashboard" },
  menu: { p_dashboard: "PANEL-STR-COV", p_transfer: "TRANSFER-STR-COV" } });
I18n._seed("v2objcov", { _meta: { version: 2, provenance: "machine", coverage: { 0: "menu.p_dashboard" } },
  menu: { p_dashboard: "PANEL-OBJ-COV", p_transfer: "TRANSFER-OBJ-COV" } });

["v2nocov", "v2strcov", "v2objcov"].forEach(function (code) {
  I18n._setCurrent(code);
  assert.strictEqual(I18n.t(k), enDict.menu.p_dashboard,
    code + ": unusable coverage falls back to English");
  assert.strictEqual(I18n.t("menu.p_transfer"), enDict.menu.p_transfer,
    code + ": unusable coverage falls back to English (second key)");
});

/* Provenance: v2 + machine is the only "machine". v1 predates the field,
 * so it reports "none" (human-only surfacing), never a false warning. */
assert.strictEqual(I18n.provenance("v2"), "machine");
assert.strictEqual(I18n.isMachineLocale("v2"), true);
assert.strictEqual(I18n.provenance("v1"), "none");
assert.strictEqual(I18n.isMachineLocale("v1"), false);

/* A v2 dict reviewed by a human is "human": the badge stays off. */
I18n._seed("v2h", { _meta: { version: 2, provenance: "human", coverage: [] }, menu: {} });
assert.strictEqual(I18n.provenance("v2h"), "human");
assert.strictEqual(I18n.isMachineLocale("v2h"), false);

/* ------------------------------------------------------------------
 * The SHIPPED dictionaries, seeded from disk — the honesty surfaces are
 * only as honest as the `_meta` the files actually carry, so this pins
 * the real state of all twelve rather than fixtures shaped like them.
 *
 * es is v2 / machine, which is what lights the badge and dual-lines the
 * signing dialog (task 8 converted it; it was v1, and a v1 dict reports
 * "none", before this). The other ten non-English dicts are still v1 and
 * must keep reporting "none" — a v1 dict carries no provenance claim, and
 * inventing one is exactly the false warning this function exists not to
 * emit. Both directions are asserted together because either alone is a
 * test that passes for the wrong reason: "es is machine" alone would still
 * pass if provenance() returned "machine" for everything, and "the others
 * are none" alone would still pass if nothing were ever machine-labelled.
 * ------------------------------------------------------------------ */
var SHIPPED = ["en", "de", "es", "fr", "hi", "it", "ja", "ko", "pt", "ru", "tr", "zh"];
var shippedMeta = {};
SHIPPED.forEach(function (code) {
  var dict = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales", code + ".json"), "utf8"));
  shippedMeta[code] = dict._meta || {};
  I18n._seed(code, dict);
});

assert.strictEqual(I18n.provenance("en"), "none", "en is the reference, never machine");
assert.strictEqual(I18n.isMachineLocale("en"), false, "en never lights the chip");
assert.strictEqual(shippedMeta.en.version, 1, "en.json is still the v1 master");

assert.strictEqual(I18n.provenance("es"), "machine", "the shipped es dict is machine-filled");
assert.strictEqual(I18n.isMachineLocale("es"), true, "…so the honesty chip lights for es");
assert.strictEqual(shippedMeta.es.version, 2, "es.json declares the v2 shape");
assert.strictEqual(shippedMeta.es.provenance, "machine",
  "es.json says machine: no human has signed any of its strings");
assert.deepStrictEqual(shippedMeta.es.verified, [],
  "es.json claims no human sign-off, and 'human' with an empty verified is fatal to the gate");

SHIPPED.filter(function (code) { return code !== "en" && code !== "es"; }).forEach(function (code) {
  assert.strictEqual(I18n.provenance(code), "none",
    code + " is still v1, and a v1 dict carries no provenance claim");
  assert.strictEqual(I18n.isMachineLocale(code), false,
    code + " must not be machine-labelled before its _meta says so");
  assert.strictEqual(shippedMeta[code].version, 1, code + ".json is still the v1 shape");
});

/* A locale nothing has ever loaded must not warn either — "none" is the
 * answer for unknown codes, so a missing dict can never fake a warning. */
assert.strictEqual(I18n.provenance("zz"), "none");

/* ------------------------------------------------------------------
 * Boot with the en master MISSING — the gap this fix closes, exercised
 * through the real boot path rather than the _seed seam.
 *
 * A second module instance, booted the way app.js boots it: saved locale
 * is es, so loadCached() fetches en (for the master) and es (for the
 * active dict). The en request 404s; es serves the REAL shipped dict.
 * Before this fix: t("menu.p_dashboard", "Dashboard") returned "Tablero"
 * and enFor("menu.p_dashboard") returned undefined, so the page rendered
 * Spanish with no English reference anywhere — and the moment es goes v2
 * the badge lights saying "machine translated" over lines that have
 * nothing to consult. After it, the English the views already pass to t()
 * is the reference.
 * ------------------------------------------------------------------ */
var offline = (function () {
  var store = { "bts-vanilla-locale-v1": "es" };
  var sb = {
    console: console,
    localStorage: {
      getItem: function (key) {
        return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null;
      },
      setItem: function (key, val) { store[key] = String(val); }
    },
    fetch: function (url) {
      if (String(url).indexOf("en.json") !== -1) return Promise.resolve({ ok: false, status: 404 });
      return Promise.resolve({ ok: true, json: function () { return Promise.resolve(esDict); } });
    }
  };
  sb.window = sb;
  vm.createContext(sb);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/i18n.js"), "utf8"), sb);
  return sb.I18n;
}());

offline.loadCached().then(function (res) {
  /* The swallowed en failure is the precondition here, not the bug: the
   * app boots and renders either way. */
  assert.strictEqual(res.ok, true, "loadCached resolves ok:true even when en fails");
  assert.strictEqual(offline.locale(), "es", "the saved locale is active");

  /* The Spanish renders — the allowlist is the active dict's own claim. */
  assert.strictEqual(offline.t(k, enDict.menu.p_dashboard), "Tablero",
    "the active locale renders while the en master is missing");

  /* …and the English reference the badge promises is there to consult. */
  assert.strictEqual(offline.enFor(k), enDict.menu.p_dashboard,
    "enFor falls back to the default t() was given (en master missing)");
  /* The badge is LIVE for es: the shipped dict is v2 / machine, so this
   * scenario — the real boot path serving the real file — lights the chip
   * over Spanish text no human has signed off. (It read "none" while
   * es.json was v1; task 8 made the file declare what the strings have
   * always been.) */
  assert.strictEqual(offline.provenance("es"), "machine",
    "the shipped es dict is machine-labelled, so the badge lights");
  assert.strictEqual(offline.isMachineLocale("es"), true,
    "…the one condition the badge and the dual-line check agree on");

  /* A key nobody rendered yet has no reference: the fallback is what t()
   * was told, so it can only speak for keys a view has already asked
   * for. Honest absence beats a guessed line. */
  assert.strictEqual(offline.enFor("no.such.key"), undefined,
    "an unrendered key has no reference to offer");

  /* The exact bad outcome the review describes — es goes v2, so the badge
   * lights "machine translated". Now the machine text renders AND the
   * English line to consult exists, because t() was handed the master
   * copy of the very key the dialog is showing. */
  offline._seed("esv2", { _meta: { version: 2, provenance: "machine", coverage: [k] },
    menu: { p_dashboard: "PANEL-V2" } });
  offline._setCurrent("esv2");
  assert.strictEqual(offline.isMachineLocale("esv2"), true, "the badge would light");
  assert.strictEqual(offline.t(k, enDict.menu.p_dashboard), "PANEL-V2",
    "the machine text is what renders");
  assert.strictEqual(offline.enFor(k), enDict.menu.p_dashboard,
    "…and the English reference beside it is there");

  console.log("OK: i18n-provenance");
}).catch(function (err) {
  /* .catch, not a second .then argument: an assertion thrown inside the
   * success handler rejects the DERIVED promise, which a sibling handler
   * never sees. Without this the failure still exits non-zero, but as an
   * uncaught exception instead of the named FAIL line. */
  console.log("FAIL: i18n-provenance — " + ((err && err.stack) ? err.stack : err));
  process.exitCode = 1;
});
