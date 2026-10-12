/* i18n-badge-failsafe-matrix-test.js — the chip must appear for EXACTLY ONE
 * shape of dictionary and nothing else, and the answer must come from the real
 * I18n.isMachineLocale(), not from a re-implementation in the chip.
 *
 * Why this file exists (review wave 1): i18n-badge-test.js answers with a FAKE
 * I18n whose provenance() is `machine ? "machine" : "human"`. A fake that can
 * only ever say two things cannot prove the gate is closed for the shapes a
 * real, machine-filled, half-migrated dictionary actually has on disk. This
 * probe drives the SHIPPED vanilla/js/i18n.js through its own test seams
 * (`_seed`, `_setCurrent`, i18n.js:291-292) and lets the real
 * provenance()/isMachineLocale() decide, then checks the chip against that
 * answer for every malformed shape a load could produce.
 *
 * The rule being pinned (i18n.js:95-100):
 *   machine  <=>  code !== "en" AND registry[code]._meta is an object
 *                AND _meta.version === 2 (a NUMBER — not "2")
 *                AND _meta.provenance === "machine" (that exact string — not
 *                "MACHINE", not true, not 1)
 * Every other shape — v1 dicts, absent/_meta: null, a string _meta, a missing
 * provenance, an unknown code — answers "none"/"human" and must paint NOTHING.
 * A badge that appears on any of them is a false warning about a dictionary
 * this app cannot even read, which is the one dishonesty the chip must never
 * commit.
 *
 * Run: node tooling/i18n-badge-failsafe-matrix-test.js   (exit 0 = green)
 */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
function load(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

/* --- minimal, faithful slot ---------------------------------------------- */
/* `children` is a live HTMLCollection-shaped view with a GETTER-ONLY `length`,
 * matching the real WebIDL attribute (i18n-badge-test.js carries the long
 * version of this note; the long version also needs the array helpers). Only
 * what mount()/refresh() touch is modelled: firstChild, removeChild,
 * appendChild, ownerDocument. */
function slot() {
  var node = {
    _kids: [], attrs: {}, style: {}, className: "", textContent: "",
    ownerDocument: doc,
    appendChild: function (c) { this._kids.push(c); return c; },
    removeChild: function (c) {
      var i = this._kids.indexOf(c);
      if (i !== -1) this._kids.splice(i, 1);
      return c;
    }
  };
  var target = {};
  Object.defineProperty(target, "length", { get: function () { return node._kids.length; }, configurable: true });
  node.children = new Proxy(target, {
    get: function (t, p) {
      if (p === "length") return node._kids.length;
      if (typeof p === "string" && /^\d+$/.test(p)) return node._kids[Number(p)];
      return t[p];
    }
  });
  Object.defineProperty(node, "firstChild", { get: function () { return this._kids.length ? this._kids[0] : null; } });
  Object.defineProperty(node, "hidden", {
    get: function () { return this.attrs.hidden === "hidden"; },
    set: function (v) { if (v) this.attrs.hidden = "hidden"; else delete this.attrs.hidden; }
  });
  return node;
}
var doc = {
  createElement: function (tag) {
    var n = slot();
    n.tagName = String(tag).toUpperCase();
    n.id = "";
    n.href = "";
    n.rel = "";
    n.target = "";
    n.setAttribute = function (k, v) { this.attrs[k] = String(v); };
    n.getAttribute = function (k) {
      return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
    };
    return n;
  },
  addEventListener: function () {}
};

/* --- the SHIPPED modules, no stubs ---------------------------------------- */
var sandbox = { document: doc, localStorage: { getItem: function () { return null; }, setItem: function () {} } };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(load("vanilla/js/i18n.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/touchable.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/dom.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/event.js"), sandbox);
vm.runInContext(load("vanilla/js/ui/i18n-badge.js"), sandbox);
var I18n = sandbox.I18n;
var I18nBadge = sandbox.I18nBadge;

var COV = ["i18n.badge_chip", "i18n.badge_label", "i18n.badge_body", "i18n.badge_details", "i18n.badge_improve"];
var MACHINE = { _meta: { version: 2, provenance: "machine", coverage: COV } };

/* Each row: [label, dict to seed under "es" (null = do not seed at all),
 * locale code to activate, whether the chip MUST appear]. */
var ROWS = [
  ["the real machine-filled v2 dict", MACHINE, "es", true],
  ["en, never seeded", null, "en", false],
  ["a v1 dict with no _meta at all (the shape every shipped locale has today)", { menu: {} }, "es", false],
  ["a v1 dict with _meta.version 1", { _meta: { version: 1, translated: COV } }, "es", false],
  ["_meta: null", { _meta: null }, "es", false],
  ["_meta.version 2 but provenance missing", { _meta: { version: 2, coverage: COV } }, "es", false],
  ["_meta.version 2, provenance \"human\" (reviewed)", { _meta: { version: 2, provenance: "human", coverage: COV } }, "es", false],
  ["_meta.version 2, provenance \"MACHINE\" (wrong case)", { _meta: { version: 2, provenance: "MACHINE", coverage: COV } }, "es", false],
  ["_meta.version 2, provenance true (boolean, not the string)", { _meta: { version: 2, provenance: true, coverage: COV } }, "es", false],
  ["_meta.version 2, provenance \"machine \" (trailing space)", { _meta: { version: 2, provenance: "machine ", coverage: COV } }, "es", false],
  ["_meta.version \"2\" as a STRING, not a number", { _meta: { version: "2", provenance: "machine", coverage: COV } }, "es", false],
  ["_meta itself a string", { _meta: "machine" }, "es", false],
  ["an unknown locale code that was never loaded", null, "zz", false],
  ["a non-string locale code", MACHINE, 42, false],
  ["an empty-string locale code", MACHINE, "", false]
];

var checks = 0;
function check(cond, label) { assert.ok(cond, label); checks++; }

ROWS.forEach(function (row) {
  var label = row[0], dict = row[1], code = row[2], mustShow = row[3];
  /* Reseed the SAME registry entry every time (undefined = "not loaded") so
   * a leaked seed from an earlier row cannot make a later row pass for the
   * wrong reason. */
  I18n._seed("es", dict === undefined ? undefined : dict);
  I18n._setCurrent(code);
  var host = slot();
  I18nBadge.mount(doc, host);
  var expectMachine = I18n.isMachineLocale(code) === true;
  check(expectMachine === mustShow,
    "the shipped registry agrees with the matrix for " + label +
    " (isMachineLocale=" + expectMachine + ", matrix=" + mustShow + ")");
  check(host._kids.length === (mustShow ? 2 : 0),
    label + " paints " + (mustShow ? "chip + note" : "NOTHING") +
    " (children=" + host._kids.length + ")");
  check(I18nBadge.visible() === mustShow,
    label + " reports visible()=" + I18nBadge.visible());
  if (mustShow) {
    check(host._kids[0].className === "i18n-badge" && host._kids[1].className === "i18n-badge-note",
      label + " paints the chip then its note, in that order");
  }
});

/* Documented edge, pinned so it cannot change silently: provenance() reads
 * ONLY _meta.version and _meta.provenance, so a dict whose `coverage` is
 * malformed still counts as machine-filled and the chip still warns. That is
 * the right answer — the dictionary IS machine-filled; the broken allowlist is
 * a separate, already-pinned concern (t() falls back to English there). */
I18n._seed("es", { _meta: { version: 2, provenance: "machine", coverage: "not-an-array" } });
I18n._setCurrent("es");
var covHost = slot();
I18nBadge.mount(doc, covHost);
check(covHost._kids.length === 2, "a malformed coverage list does not un-warn a machine dict (chip still shown)");

/* And the honest inverse, pinned: a machine dict whose coverage does NOT list
 * the chip's own keys renders the chip with the English defaults (t() falls
 * back to en.json / the call site), never a blank panel. */
I18n._seed("es", { _meta: { version: 2, provenance: "machine", coverage: [] } });
I18n._setCurrent("es");
var bareCov = slot();
I18nBadge.mount(doc, bareCov);
check(bareCov._kids.length === 2 && bareCov._kids[0].textContent === "i18n",
  "an un-allowlisted chip still renders the English face 'i18n', not the key id");
check(bareCov._kids[1]._kids[0].textContent.indexOf("machine") !== -1,
  "and the panel falls back to the English warning sentence, never to a blank or a key id");

console.log("i18n-badge-failsafe-matrix: " + checks + " checks passed (" + ROWS.length + " dictionary shapes)");