/* risk-text-test: the dual-line honesty surface on the signing path, so its
 * three modes are pinned — dual-line when machine + key + a differing English
 * source, plain when there is no English reference or none that differs, and
 * plain when the locale is verified/human. The asterisk must be a real button
 * with a 44px touch floor and aria-expanded/aria-controls (no hover-only
 * affordance, AGENTS.md §3.6), and the disclosure must actually toggle.
 *
 * Two notes on the harness, both loadings rather than fakes:
 *   1. utils/dom.js, utils/touchable.js and utils/event.js are the SHIPPED
 *      modules, loaded as-is. The brief's draft stubbed DOM.el/touchable and
 *      a global `Event`; the real globals are `touchable` and `EventDelegate`
 *      (Event is reserved for the DOM constructor), and the delegated handler
 *      receives the matched element as its SECOND argument. Stubbing them
 *      would have hidden exactly the wiring Task 4 depends on.
 *   2. The fake document supplies only createElement + addEventListener, and
 *      reflects `type`/`hidden` to attributes the way real elements do, so
 *      `[hidden]` CSS and getAttribute assertions see the same truth.
 * Anything richer than this is the browser probe's job (tooling/visual/). */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
function load(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

var clickListeners = [];
function el(tag) {
  var node = {
    tagName: String(tag).toUpperCase(),
    children: [], attrs: {}, style: {},
    className: "", textContent: "", parentNode: null,
    setAttribute: function (k, v) { this.attrs[k] = String(v); },
    getAttribute: function (k) {
      return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
    },
    hasAttribute: function (k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); },
    removeAttribute: function (k) { delete this.attrs[k]; },
    appendChild: function (c) { if (c) c.parentNode = this; this.children.push(c); return c; },
    addEventListener: function () {}
  };
  var hiddenFlag = false;
  Object.defineProperty(node, "type", {
    get: function () { return this.attrs.type === undefined ? "" : this.attrs.type; },
    set: function (v) { this.attrs.type = String(v); }
  });
  Object.defineProperty(node, "hidden", {
    get: function () { return hiddenFlag; },
    set: function (v) { hiddenFlag = !!v; if (v) { this.attrs.hidden = ""; } else { delete this.attrs.hidden; } }
  });
  return node;
}

var document = {
  createElement: el,
  addEventListener: function (type, fn) { if (type === "click") clickListeners.push(fn); },
  removeEventListener: function (type, fn) {
    if (type !== "click") return;
    var i = clickListeners.indexOf(fn);
    if (i !== -1) clickListeners.splice(i, 1);
  }
};
function click(node) {
  clickListeners.forEach(function (fn) { fn({ target: node, currentTarget: document }); });
}

var sandbox = { document: document };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(load("vanilla/js/utils/touchable.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/dom.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/event.js"), sandbox);

/* Fake I18n mirroring the shipped Task 2 contract: locale() names the active
 * code, isMachineLocale(code) takes that code (calling it with no argument is
 * how a caller silently gets false), enFor(key) may be undefined when neither
 * the en master nor a recorded t() default knows the key. */
var localeCode = "es";
var machine = true;
sandbox.I18n = {
  locale: function () { return localeCode; },
  isMachineLocale: function (code) { return machine && code !== "en"; },
  enFor: function (k) {
    if (k === "unlockconfirm.confirm") return "Unlock to sign";
    if (k === "menu.dashboard") return "Dashboard";
    return undefined;
  }
};

vm.runInContext(load("vanilla/js/ui/risk-text.js"), sandbox);
var RiskText = sandbox.RiskText;

function find(node, cls) {
  if (!node) return null;
  if (node.className === cls) return node;
  var kids = node.children || [];
  for (var i = 0; i < kids.length; i++) {
    var hit = find(kids[i], cls);
    if (hit) return hit;
  }
  return null;
}

/* 1. machine locale + high-risk key -> dual-line with asterisk. */
var node = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(node.className, "i18n-risk", "dual-line wrapper");
var native = find(node, "i18n-risk-native");
assert.ok(native, "native line exists");
assert.strictEqual(native.textContent, "Desbloquear para firmar", "native text is what was passed");
var star = find(node, "i18n-risk-star");
assert.ok(star, "asterisk exists");
assert.strictEqual(star.tagName, "BUTTON", "asterisk is a real button");
assert.strictEqual(star.attrs["aria-expanded"], "false", "starts collapsed");
assert.strictEqual(star.attrs.type, "button", "never submits a form");
assert.ok(star.getAttribute("aria-controls"), "aria-controls names the panel");
assert.ok(star.style.minHeight === "44px" && star.style.minWidth === "44px",
  "touch floor applied by the shared touchable()");
var en = find(node, "i18n-risk-en");
assert.ok(en, "english line exists");
assert.strictEqual(en.hidden, true, "english starts hidden");
assert.strictEqual(en.id, star.getAttribute("aria-controls"), "aria-controls points at the english line");
assert.ok(en.textContent.indexOf("Unlock to sign") !== -1, "english text is the reference");
var more = find(node, "i18n-risk-more");
assert.ok(more, "the limitations link is reachable from the line itself");
assert.strictEqual(more.tagName, "A", "limitations link is an anchor");
assert.ok(String(more.href).indexOf("#/help/translation-limitations") !== -1,
  "limitations link points at the article");
assert.strictEqual(more.parentNode, node, "link lives on the wrapper, not inside the english text");

/* 2. no key -> plain (dynamic values: amounts, ids, symbols). */
var plain = RiskText.render(document, "1.234,56 BTS", null);
assert.strictEqual(plain.className, "i18n-risk-plain", "dynamic values stay plain");
assert.strictEqual(plain.textContent, "1.234,56 BTS", "plain keeps the text");

/* 3. the displayed text IS the english -> plain (nothing to disclose). */
var same = RiskText.render(document, "Unlock to sign", "unlockconfirm.confirm");
assert.strictEqual(same.className, "i18n-risk-plain", "no dual-line when text already is the english");

/* 4. human/verified locale -> plain even for a high-risk key. */
machine = false;
var human = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(human.className, "i18n-risk-plain", "verified locales lose the asterisk");
assert.strictEqual(RiskText.isActive(), false, "isActive is false off a machine locale");

/* en is never machine-filled: an active en locale must never double up. */
machine = true;
localeCode = "en";
var enLocale = RiskText.render(document, "Unlock to sign", "unlockconfirm.confirm");
assert.strictEqual(enLocale.className, "i18n-risk-plain", "the english locale needs no reference line");
localeCode = "es";
assert.strictEqual(RiskText.isActive(), true, "isActive is true on a machine locale");

/* 5. unknown english source -> plain, never an empty english line
 *    (I18n.enFor returns undefined when the master and the recorded t()
 *    default both miss — a missing reference beats a wrong one). */
var unknown = RiskText.render(document, "Texte dynamique", "some.key.nobody.knows");
assert.strictEqual(unknown.className, "i18n-risk-plain", "no english source degrades to plain");
assert.strictEqual(unknown.textContent, "Texte dynamique", "the degraded text is untouched");

/* 6. the disclosure toggles through the shared delegated listener. */
var t1 = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
var s1 = find(t1, "i18n-risk-star");
var e1 = find(t1, "i18n-risk-en");
var id1 = e1.id;
click(s1);
assert.strictEqual(s1.getAttribute("aria-expanded"), "true", "first tap expands");
assert.strictEqual(e1.hidden, false, "first tap reveals the english");
click(s1);
assert.strictEqual(s1.getAttribute("aria-expanded"), "false", "second tap collapses");
assert.strictEqual(e1.hidden, true, "second tap hides it again");

/* ids are unique, so one disclosure never drives another's panel. */
var t2 = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
var e2 = find(t2, "i18n-risk-en");
assert.notStrictEqual(e2.id, id1, "each dual-line gets its own panel id");
click(find(t2, "i18n-risk-star"));
assert.strictEqual(e1.hidden, true, "opening the second panel leaves the first closed");

/* exactly one delegated listener for the whole app, however many renders. */
assert.strictEqual(clickListeners.length, 1, "the disclosure binds one delegated click listener");

/* 7. wrap is the render alias for row/cell use, and odd input never throws. */
assert.strictEqual(RiskText.wrap, RiskText.render, "wrap is the render alias");
assert.strictEqual(typeof RiskText.isActive, "function", "isActive exists");
assert.strictEqual(RiskText.render(document, "", "unlockconfirm.confirm").className,
  "i18n-risk-plain", "empty text degrades to plain");
assert.strictEqual(RiskText.render(document, null, null).textContent, "", "null text renders empty");
assert.strictEqual(RiskText.render(document, 42, null).textContent, "42", "non-string text is stringified");
assert.strictEqual(RiskText.render(document, "x", 42).className, "i18n-risk-plain",
  "a non-string key is not a key");

console.log("OK: risk-text");