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
 *   3. Sections 8-9 stand up two more sandboxes with parts of that harness
 *      MISSING on purpose (no DOM global; no document at all) — the module
 *      claims it never throws and never answers null, and that claim is only
 *      testable away from the fully-loaded sandbox.
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

/* Fake I18n mirroring the shipped Task 2 contract (i18n.js:95-109) EXACTLY:
 * locale() names the active code, isMachineLocale(code) takes that code, and
 * enFor(key) may be undefined when neither the en master nor a recorded t()
 * default knows the key.
 *
 * The isMachineLocale fake is deliberately STRICT, because a permissive one
 * hides the bug this widget exists to be careful about: the real function is
 * provenance(code) === "machine", and provenance answers "none" for anything
 * that is not a loaded non-en locale — a non-string code included. A fake
 * written as `machine && code !== "en"` says true for undefined, so calling
 * isMachineLocale() with no argument (the mistake this module must not make)
 * still renders dual-line and the suite stays GREEN over the real defect.
 * Faithful terms, therefore: a non-empty string code that is not "en". */
var localeCode = "es";
var machine = true;
var enForCalls = 0;
/* One factory, so the degraded sandboxes below get the SAME contract instead
 * of a second, laxer copy. */
function fakeI18n() {
  return {
    locale: function () { return localeCode; },
    isMachineLocale: function (code) {
      return machine && typeof code === "string" && !!code && code !== "en";
    },
    enFor: function (k) {
      enForCalls += 1;
      if (k === "unlockconfirm.confirm") return "Unlock to sign";
      if (k === "menu.dashboard") return "Dashboard";
      return undefined;
    }
  };
}
sandbox.I18n = fakeI18n();

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
/* The en reference is byte-exact, not "contains the words": the panel shows
 * the en master string and nothing else (the limitations link is a SIBLING of
 * the panel, asserted below). */
assert.strictEqual(en.textContent, "Unlock to sign", "english text is the reference, byte-exact");
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
/* The ACTIVE LOCALE has to be what decides, so prove it with a pair where the
 * text is NOT the english source. The assertion above passes on the "text
 * already is the english" short-circuit, which holds whatever locale the
 * module reads; this one cannot. Same key, same differing text, plain here
 * and dual-line one step below — the locale is the only variable, so a module
 * that hardcoded a code (or ignored I18n.locale() entirely) fails both. */
var enSamePair = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(enSamePair.className, "i18n-risk-plain",
  "under en, a high-risk key whose text differs from the en master stays plain");
assert.strictEqual(RiskText.isActive(), false, "isActive is false when the active locale is en");
localeCode = "es";
var esSamePair = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(esSamePair.className, "i18n-risk",
  "the identical pair dual-lines once the active locale is machine-filled");
assert.strictEqual(RiskText.isActive(), true, "isActive is true on a machine locale");

/* 5. unknown english source -> plain, never an empty english line
 *    (I18n.enFor returns undefined when the master and the recorded t()
 *    default both miss — a missing reference beats a wrong one). */
var unknown = RiskText.render(document, "Texte dynamique", "some.key.nobody.knows");
assert.strictEqual(unknown.className, "i18n-risk-plain", "no english source degrades to plain");
assert.strictEqual(unknown.textContent, "Texte dynamique", "the degraded text is untouched");

/* 6. the disclosure toggles through the shared delegated listener. */
var t1 = RiskText.render(document, "Desbloquear para firma", "unlockconfirm.confirm");
var s1 = find(t1, "i18n-risk-star");
var e1 = find(t1, "i18n-risk-en");
var id1 = e1.id;
/* The class IS the CSS: `.i18n-risk.is-open .i18n-risk-more { display:inline }`
 * in app.css is the only thing that reveals the "About these translations"
 * link, so a module that stopped toggling it would leave that link as
 * permanently invisible markup while aria/hidden assertions still passed. */
assert.ok(String(t1.className).indexOf("is-open") === -1, "wrapper starts without the open class");
click(s1);
assert.strictEqual(s1.getAttribute("aria-expanded"), "true", "first tap expands");
assert.strictEqual(e1.hidden, false, "first tap reveals the english");
assert.ok(String(t1.className).split(/\s+/).indexOf("is-open") !== -1,
  "first tap puts is-open on the wrapper — the class app.css needs for .i18n-risk-more");
click(s1);
assert.strictEqual(s1.getAttribute("aria-expanded"), "false", "second tap collapses");
assert.strictEqual(e1.hidden, true, "second tap hides it again");
assert.ok(String(t1.className).split(/\s+/).indexOf("is-open") === -1,
  "second tap removes is-open, and never leaves the class behind twice");

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

/* 8. ONE English lookup per dual-line line. The decision compares the en
 *    source against the text, and the panel then renders that same source; two
 *    lookups can disagree (the master could be re-read between them), which
 *    would put a line's panel out of sync with the reason it was rendered. */
enForCalls = 0;
var once = RiskText.render(document, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.strictEqual(once.className, "i18n-risk", "the counted render dual-lined");
assert.strictEqual(enForCalls, 1, "the English source is resolved once and reused for the panel");
assert.strictEqual(find(once, "i18n-risk-en").textContent, "Unlock to sign",
  "the panel shows the source the decision compared against");

/* 9. a missing helper degrades instead of throwing. Two harnesses, neither of
 *    which any real page can be: (a) no DOM global (utils/dom.js not loaded)
 *    with a document present, and (b) no document at all. The module header
 *    claims "never throws", so both must answer a node. */

/* (a) document present, DOM absent. */
var bareDoc = { createElement: el, addEventListener: function () {} };
var bare = { document: bareDoc, I18n: fakeI18n() };
bare.window = bare;
vm.createContext(bare);
vm.runInContext(load("vanilla/js/ui/risk-text.js"), bare);
var bareOut = bare.RiskText.render(bareDoc, "Desbloquear para firma", "unlockconfirm.confirm");
assert.ok(bareOut, "no DOM global must not throw and must still answer a node");
assert.strictEqual(bareOut.className, "i18n-risk",
  "without the DOM helper the dual-line line still renders (raw createElement)");
assert.ok(find(bareOut, "i18n-risk-star"), "the asterisk survives a missing DOM helper");
assert.ok(find(bareOut, "i18n-risk-en"), "the english panel survives a missing DOM helper");
assert.strictEqual(bare.RiskText.render(bareDoc, "Unlock to sign", "unlockconfirm.confirm").className,
  "i18n-risk-plain", "and the plain path survives a missing DOM helper too");

/* (b) no document at all. Task 4 mounts this straight into ConfirmDialog with
 *     appendChild, which stringifies a null return into the dialog as the
 *     visible text "null" — so the degraded answer is an EMPTY plain wrapper,
 *     never null. */
var headless = {};
headless.window = headless;
vm.createContext(headless);
vm.runInContext(load("vanilla/js/ui/risk-text.js"), headless);
var noDoc = headless.RiskText.render(undefined, "Desbloquear para firmar", "unlockconfirm.confirm");
assert.ok(noDoc, "no document must not throw and must not answer null");
assert.strictEqual(noDoc.className, "i18n-risk-plain", "the no-document floor is a plain wrapper");
assert.strictEqual(noDoc.textContent, "", "and it is empty — nothing is rendered, rather than \"null\"");
assert.ok(headless.RiskText.isActive() === false, "isActive is false without I18n");

/* 10. Both of this widget's own strings are KEYED (Task 6 closed the two
 *     English literals). Checked two ways, because either alone is gameable:
 *     the source must name the keys, and a render must actually USE them — a
 *     module that keeps a hardcoded string beside a t() call passes a
 *     grep-only check and still shows English to every non-English reader. */
(function () {
  var src = load("vanilla/js/ui/risk-text.js");
  var KEYS = [
    ["i18n.risk_show_english", "Show the English reference for this line"],
    ["i18n.risk_about_translations", "About these translations"]
  ];
  KEYS.forEach(function (pair) {
    var call = new RegExp("t\\(\\s*\"" + pair[0] + "\"\\s*,\\s*\"" + pair[1] + "\"\\s*\\)");
    assert.ok(call.test(src), "the string is resolved through t(" + pair[0] + ")");
    var occurrences = src.split(pair[1]).length - 1;
    assert.strictEqual(occurrences, 1,
      "the English text survives only as that t() default, not as a second literal: " + pair[1]);
  });

  /* A locale-aware sandbox: same module, an I18n whose t() answers a
   * translation. Fresh document + listener array so the "one delegated
   * listener" assertion above keeps counting the original sandbox's. */
  function doc2() {
    return { createElement: el, addEventListener: function () {},
      removeEventListener: function () {} };
  }
  var keyed = { locale: function () { return "es"; },
    isMachineLocale: function (c) { return c === "es"; },
    enFor: function (k) { return k === "unlockconfirm.confirm" ? "Unlock to sign" : undefined; },
    t: function (k, dflt) {
      return k === "i18n.risk_show_english" ? "Mostrar la referencia en inglés de esta línea"
        : k === "i18n.risk_about_translations" ? "Acerca de estas traducciones"
        : dflt;
    } };
  var box = { document: doc2(), I18n: keyed };
  box.window = box;
  vm.createContext(box);
  vm.runInContext(load("vanilla/js/utils/touchable.js"), box);
  vm.runInContext(load("vanilla/js/utils/dom.js"), box);
  vm.runInContext(load("vanilla/js/utils/event.js"), box);
  vm.runInContext(load("vanilla/js/ui/risk-text.js"), box);
  var line = box.RiskText.render(box.document, "Desbloquear para firmar", "unlockconfirm.confirm");
  assert.strictEqual(line.className, "i18n-risk", "the keyed sandbox dual-lines");
  assert.strictEqual(find(line, "i18n-risk-star").getAttribute("aria-label"),
    "Mostrar la referencia en inglés de esta línea",
    "the asterisk's accessible name comes from the dictionary, not a literal");
  assert.strictEqual(find(line, "i18n-risk-more").textContent, "Acerca de estas traducciones",
    "the article link's label comes from the dictionary, not a literal");
  /* …and a locale with no value for the key still renders English, because the
   * t() default is kept at the call site (a bare t(key) would show the key). */
  var bareI18n = { locale: function () { return "de"; },
    isMachineLocale: function (c) { return c === "de"; },
    enFor: function () { return "Unlock to sign"; },
    t: function (k, dflt) { return dflt; } };
  var box2 = { document: doc2(), I18n: bareI18n };
  box2.window = box2;
  vm.createContext(box2);
  vm.runInContext(load("vanilla/js/utils/dom.js"), box2);
  vm.runInContext(load("vanilla/js/ui/risk-text.js"), box2);
  var line2 = box2.RiskText.render(box2.document, "Entsperren zum Signieren", "unlockconfirm.confirm");
  assert.strictEqual(find(line2, "i18n-risk-star").getAttribute("aria-label"),
    "Show the English reference for this line",
    "an untranslated locale falls back to English, never to the key name");
  assert.strictEqual(find(line2, "i18n-risk-more").textContent, "About these translations",
    "and the article link label likewise");
})();

console.log("OK: risk-text");