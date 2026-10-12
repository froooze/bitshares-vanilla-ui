/* i18n-badge-no-dom-test.js — the module header promises "a missing DOM helper
 * degrades the chip instead of throwing". Review wave 1 / Important 1 proved
 * that promise FALSE on a real browser: clearHost()'s fallback ended with
 * `node.children.length = 0`, and HTMLCollection.length is a readonly WebIDL
 * attribute, so in this strict-mode module that assignment is a TypeError. The
 * error escaped the unguarded `clearHost(host)` inside refresh()'s catch and
 * went out of refresh() and mount(), taking the header with it.
 *
 * This probe is the durable form of that proof, and it is sharp in BOTH
 * directions:
 *   1. a canary re-runs the removed line against the fake slot and requires it
 *      to THROW — so if the harness ever regresses to a plain array (writable
 *      length) the canary fails loudly instead of the probe quietly proving
 *      nothing;
 *   2. the same assignment is re-run in SLOPPY mode and required NOT to throw,
 *      which is why the real utils/dom.js is unaffected today (it has no
 *      "use strict") and why the harness models the getter rather than a
 *      hand-written throw;
 *   3. with utils/dom.js genuinely absent, mount() and refresh() must not throw
 *      AND the chip must still render — the shipped assertion that was false;
 *   4. a slot whose own removeChild throws must degrade to silence without an
 *      exception escaping refresh()'s cleanup path.
 *
 * Run: node tooling/i18n-badge-no-dom-test.js   (exit 0 = green)
 */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
var SRC = fs.readFileSync(path.join(ROOT, "vanilla/js/ui/i18n-badge.js"), "utf8");

/* --- the fake DOM --------------------------------------------------------- */
/* `children` is a live HTMLCollection-shaped view whose `length` is a
 * GETTER-ONLY accessor, exactly as the real platform exposes it. Reads and
 * index access go to the live child list; a write to `length` is handed to the
 * engine, which then applies the caller's own strict/sloppy semantics. */
function slot(opts) {
  opts = opts || {};
  var node = {
    _kids: [], attrs: {}, style: {}, className: "", textContent: "",
    id: "", href: "", rel: "", target: "",
    ownerDocument: doc,
    appendChild: function (c) { this._kids.push(c); return c; },
    removeChild: function (c) {
      if (opts.removeChildThrows) throw new Error("removeChild exploded");
      var i = this._kids.indexOf(c);
      if (i !== -1) this._kids.splice(i, 1);
      return c;
    },
    setAttribute: function (k, v) { this.attrs[k] = String(v); },
    getAttribute: function (k) {
      return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
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
  var hiddenFlag = false;
  Object.defineProperty(node, "hidden", {
    get: function () { return hiddenFlag; },
    set: function (v) { hiddenFlag = !!v; }
  });
  return node;
}
var doc = {
  createElement: function (tag) { var n = slot(); n.tagName = String(tag).toUpperCase(); return n; },
  addEventListener: function () {}
};

/* A machine-filled dict, seeded through the shipped i18n.js test seams. */
function boot(withDomHelper) {
  var box = {
    document: doc,
    localStorage: { getItem: function () { return null; }, setItem: function () {} },
    I18n: null
  };
  box.window = box;
  vm.createContext(box);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/i18n.js"), "utf8"), box);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/utils/touchable.js"), "utf8"), box);
  /* utils/dom.js is THE THING BEING ABSENT: no DOM global exists in this
   * sandbox, so every fallback path in the chip is the live one. */
  if (withDomHelper) vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/utils/dom.js"), "utf8"), box);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "vanilla/js/utils/event.js"), "utf8"), box);
  vm.runInContext(SRC, box);
  box.I18n._seed("es", { _meta: { version: 2, provenance: "machine", coverage: [
    "i18n.badge_chip", "i18n.badge_label", "i18n.badge_body",
    "i18n.badge_details", "i18n.badge_improve"] } });
  box.I18n._setCurrent("es");
  return box;
}

/* --- 1/2. the canary: the harness must be sharp in both directions -------- */
/* Strict mode is what ui/i18n-badge.js declares, and what made the defect a
 * thrown TypeError rather than a silent no-op. The error is compared by NAME,
 * not by constructor: it is raised inside a vm realm, so its TypeError is a
 * different realm's class than this file's. */
var strictCanary = vm.runInNewContext('"use strict"; (function (n) { n.children.length = 0; })', {});
var strictErr = null;
try { strictCanary(slot()); } catch (e) { strictErr = e; }
assert.ok(strictErr && strictErr.name === "TypeError",
  "canary: a strict-mode `children.length = 0` throws TypeError, as it does in Chromium " +
  "(got " + (strictErr ? strictErr.name + ": " + strictErr.message : "no throw") + ")");
/* Sloppy mode is why the same line in utils/dom.js (no \"use strict\") is a
 * silent no-op today — the harness must reproduce that too, or it would be
 * stricter than the platform and would report failures browsers never see. */
var sloppyCanary = vm.runInNewContext('(function (n) { n.children.length = 0; return "no-throw"; })', {});
assert.strictEqual(sloppyCanary(slot()), "no-throw",
  "canary: the same assignment in sloppy mode is a silent no-op, as in a real browser");

/* --- 3. no DOM global: the chip still renders, nothing throws -------------- */
var box = boot(false);
assert.strictEqual(typeof box.DOM, "undefined", "utils/dom.js really is absent in this sandbox");
var host = slot();
assert.doesNotThrow(function () { box.I18nBadge.mount(doc, host); },
  "mount() without the DOM helper must not throw out of the header");
assert.strictEqual(host._kids.length, 2, "without the DOM helper the chip still renders");
assert.strictEqual(host._kids[0].className, "i18n-badge", "and it is the chip");
assert.strictEqual(host._kids[1].className, "i18n-badge-note", "with its panel");
assert.strictEqual(box.I18nBadge.visible(), true, "and visible() agrees");
assert.doesNotThrow(function () { box.I18nBadge.refresh(); }, "refresh() without the DOM helper must not throw");
assert.strictEqual(host._kids.length, 2, "a repaint rebuilds the same two nodes");

/* Mounting over a slot that already holds the chip exercises the fallback
 * clearHost for real — the exact call the defect lived in. */
assert.doesNotThrow(function () { box.I18nBadge.mount(doc, host); },
  "re-mounting over a populated slot must not throw (the fallback clearHost path)");
assert.strictEqual(host._kids.length, 2, "and leaves exactly chip + note, never a doubled tree");

/* --- 4. a slot that throws on clear must degrade to silence ---------------- */
/* refresh()'s cleanup runs from inside its own catch; if THAT call is not
 * guarded, a cleanup failure escapes refresh() and mount() — the second half of
 * the Important 1 defect. */
var hostile = boot(false);
var bad = slot({ removeChildThrows: true });
bad._kids.push(slot());           /* something for clearHost to try to remove */
assert.doesNotThrow(function () { hostile.I18nBadge.mount(doc, bad); },
  "a slot whose removeChild throws must not escape mount()");
assert.strictEqual(hostile.I18nBadge.visible(), false,
  "and it must report nothing visible rather than claiming a chip it could not paint");
assert.doesNotThrow(function () { hostile.I18nBadge.refresh(); },
  "nor may the failure escape refresh()");

/* The same guarantee with the helper present, so the guarded cleanup is not
 * accidentally tied to the no-DOM path. */
var withHelper = boot(true);
var bad2 = slot({ removeChildThrows: true });
bad2._kids.push(slot());
assert.doesNotThrow(function () { withHelper.I18nBadge.mount(doc, bad2); },
  "the guarded cleanup holds with utils/dom.js loaded too");
assert.strictEqual(withHelper.I18nBadge.visible(), false, "and visible() stays honest");

/* --- 5. the module no longer contains the removed fallback ----------------- */
/* A source-level guard, so the line cannot be reintroduced in a shape the
 * harness would not notice (e.g. behind a typeof probe). Comments are stripped
 * first: the prose that explains why the line was removed mentions it. */
var CODE = SRC.replace(/\/\*[\s\S]*?\*\//g, " ").replace(/^\s*\/\/.*$/gm, " ");
assert.strictEqual(CODE.indexOf("children.length"), -1,
  "no executable code writes to an HTMLCollection length (children.length)");

console.log("i18n-badge-no-dom: green (no DOM helper, chip renders, nothing throws)");