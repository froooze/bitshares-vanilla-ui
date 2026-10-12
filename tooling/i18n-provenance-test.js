/* i18n-provenance-test: the honesty surfaces all ask the same three
 * questions (is this locale machine-filled, what is the English source,
 * is this key verified). They must answer from the registry, never from
 * a re-read of the file, so all three are pinned here.
 *
 * Two places where the task-2 brief's draft test could not run as written
 * against the shipped code (both resolved toward the real code path, both
 * documented in .superpowers/sdd/task-2-report.md):
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
 *      the value against en.json. */
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

/* Seed the REAL English master (the dict loadCached fetches, read
 * Node-side — no network, no second copy of the data in this test). */
var enDict = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/en.json"), "utf8"));
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

console.log("OK: i18n-provenance");