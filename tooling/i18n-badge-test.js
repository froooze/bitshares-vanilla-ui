/* i18n-badge-test: the header honesty chip — the ONE persistent surface that
 * says "this language is machine-written" for the whole app (plan Task 5,
 * spec §4.3). Three properties are pinned here:
 *
 *   1. ZERO PIXELS for everyone else. English, a human-reviewed dict and an
 *      unloaded/unknown dict must leave the header slot with NO children at
 *      all (the extension shield-badge precedent, docs/vanilla-ui-dialog.md
 *      §2: "badge renders only when protected; in-browser users pay zero
 *      pixels"). A badge that stays in the DOM and merely hides would still
 *      cost a layout box, a tab stop and a screen-reader announcement.
 *   2. NEVER LIES. I18n.isMachineLocale answers false for anything it cannot
 *      prove — en, an unloaded dict, an unknown code, a v1 dict — so an
 *      unreadable dictionary can never raise a warning about itself.
 *   3. NEVER DISMISSIBLE. No storage write may happen, ever: the note may
 *      collapse on a tap, but a warning the user can lose is not a warning.
 *
 * Two notes on the harness, both loadings rather than fakes:
 *   1. utils/dom.js, utils/touchable.js and utils/event.js are the SHIPPED
 *      modules, loaded as-is. The brief's draft stubbed DOM.touchable and a
 *      global `Event`; the real globals are the bare `touchable` and
 *      `EventDelegate` (Event is reserved for the DOM constructor), and the
 *      delegated handler receives the matched element as its SECOND argument.
 *      Stubbing them would have hidden exactly the wiring this module needs.
 *      The fake ELEMENT addEventListener is a deliberate no-op, so a module
 *      that bound the chip privately (instead of delegating) leaves the
 *      disclosure inert and this suite goes red.
 *   2. The fake I18n mirrors i18n.js:95-109 EXACTLY — locale() names the
 *      active code, isMachineLocale(code) TAKES THAT CODE and answers
 *      provenance(code) === "machine", and provenance answers "none" for en
 *      and for any code with no loaded dict. A permissive fake
 *      (`machine && code !== "en"`) says true for undefined, so calling
 *      isMachineLocale() bare — the mistake this module must not make — would
 *      still render the chip and the suite would stay GREEN over the defect.
 */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
function load(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

/* --- fake DOM ---------------------------------------------------------- */
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
    removeChild: function (c) {
      var i = this.children.indexOf(c);
      if (i !== -1) this.children.splice(i, 1);
      return c;
    },
    /* Deliberately inert: the shared delegated binder (EventDelegate) is the
     * only path that can make this test's click() reach a handler. */
    addEventListener: function () {}
  };
  var hiddenFlag = false;
  Object.defineProperty(node, "firstChild", {
    get: function () { return this.children.length ? this.children[0] : null; }
  });
  Object.defineProperty(node, "type", {
    get: function () { return Object.prototype.hasOwnProperty.call(this.attrs, "type") ? this.attrs.type : ""; },
    set: function (v) { this.attrs.type = String(v); }
  });
  Object.defineProperty(node, "hidden", {
    get: function () { return hiddenFlag; },
    set: function (v) {
      hiddenFlag = !!v;
      if (v) { this.attrs.hidden = ""; } else { delete this.attrs.hidden; }
    }
  });
  return node;
}

function byId(node, id) {
  if (!node) return null;
  if (node.id === id) return node;
  var kids = node.children || [];
  for (var i = 0; i < kids.length; i++) {
    var hit = byId(kids[i], id);
    if (hit) return hit;
  }
  return null;
}
var document = {
  createElement: el,
  addEventListener: function (type, fn) { if (type === "click") clickListeners.push(fn); },
  removeEventListener: function (type, fn) {
    if (type !== "click") return;
    var i = clickListeners.indexOf(fn);
    if (i !== -1) clickListeners.splice(i, 1);
  },
  getElementById: function (id) {
    var hosts = Object.keys(hosts);
    for (var i = 0; i < hosts.length; i++) {
      var hit = byId(hosts[hosts[i]], id);
      if (hit) return hit;
    }
    return null;
  }
};
var hosts = {};
function click(node) {
  clickListeners.forEach(function (fn) { fn({ target: node, currentTarget: document }); });
}
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

/* --- fake storage ------------------------------------------------------ */
var storageCalls = [];
var localStorage = {
  getItem: function (k) { storageCalls.push("getItem " + k); return null; },
  setItem: function (k, v) { storageCalls.push("setItem " + k + "=" + v); },
  removeItem: function (k) { storageCalls.push("removeItem " + k); },
  clear: function () { storageCalls.push("clear"); }
};

/* --- fake I18n (mirrors i18n.js:95-109 + t()) -------------------------- */
var localeCode = "en";
/* code -> dict. Absent = not in the registry, which provenance answers "none"
 * for — the real "we cannot read this dictionary" case. */
var dicts = { es: { machine: true }, de: { machine: false } };
var tCalls = [];
function prov(code) {
  if (code === "en") return "none";
  var d = dicts[code];
  if (!d) return "none";
  return d.machine ? "machine" : "human";
}
function fakeI18n() {
  return {
    locale: function () { return localeCode; },
    provenance: prov,
    isMachineLocale: function (code) { return prov(code) === "machine"; },
    t: function (key, dflt) { tCalls.push(key); return "«" + key + "»"; },
    enFor: function () { return undefined; }
  };
}

/* --- load the shipped helpers + the module ---------------------------- */
var sandbox = { document: document, localStorage: localStorage, I18n: fakeI18n() };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(load("vanilla/js/utils/touchable.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/dom.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/event.js"), sandbox);
vm.runInContext(load("vanilla/js/ui/i18n-badge.js"), sandbox);
var B = sandbox.I18nBadge;

var host = el("div");
hosts.host = host;

/* --- 1. the zero-pixel contract ---------------------------------------- */
assert.strictEqual(typeof B.mount, "function", "mount exists");
assert.strictEqual(typeof B.refresh, "function", "refresh exists");
assert.strictEqual(typeof B.visible, "function", "visible exists");

localeCode = "en";
B.mount(document, host);
assert.strictEqual(host.children.length, 0, "English pays zero pixels — no element at all");
assert.strictEqual(B.visible(), false, "English is not a machine locale");

localeCode = "zz";  /* shipped-looking but never loaded */
B.mount(document, host);
assert.strictEqual(host.children.length, 0, "an unloaded dict shows nothing rather than a warning about a dict we cannot read");
assert.strictEqual(B.visible(), false, "an unloaded dict is not machine provenance");

localeCode = "de";  /* loaded, human-reviewed */
B.mount(document, host);
assert.strictEqual(host.children.length, 0, "a human-reviewed dict pays zero pixels");
assert.strictEqual(B.visible(), false, "a human-reviewed dict is not machine provenance");

/* --- 2. machine locale: chip + note ------------------------------------ */
tCalls = [];
localeCode = "es";
B.mount(document, host);
assert.strictEqual(B.visible(), true, "a machine-filled dict is visible");
assert.strictEqual(host.children.length, 2, "chip + note, nothing else");
var chip = host.children[0];
var note = host.children[1];
assert.strictEqual(chip.className, "i18n-badge", "the chip is the chip class");
assert.strictEqual(chip.tagName, "BUTTON", "a real <button>, so keyboard + AT reach it");
assert.strictEqual(chip.getAttribute("type"), "button", "never submits anything");
assert.strictEqual(chip.getAttribute("aria-expanded"), "false", "collapsed by default");
assert.ok(chip.getAttribute("aria-controls"), "aria-controls names the note");
assert.strictEqual(chip.getAttribute("aria-controls"), note.id, "and names THIS note");
assert.ok(chip.getAttribute("aria-label"), "the chip's two-letter face has an accessible name");
assert.strictEqual(chip.textContent, "«i18n.badge_chip»", "even the chip's face is a keyed string");
assert.ok(chip.style.minHeight === "44px" && chip.style.minWidth === "44px",
  "the shared touchable() floor is applied to the chip");
assert.strictEqual(note.className, "i18n-badge-note", "the note carries its class");
assert.strictEqual(note.hidden, true, "the note starts hidden");
assert.strictEqual(note.getAttribute("aria-live"), "polite", "opening it is announced");

["i18n.badge_chip", "i18n.badge_label", "i18n.badge_body",
  "i18n.badge_details", "i18n.badge_improve"].forEach(function (k) {
  assert.ok(tCalls.indexOf(k) !== -1, "every user-visible string resolves through t(): " + k);
});

/* Both promises the warning makes must be real links in the DOM. */
var body = find(note, "i18n-badge-text");
assert.ok(body, "the warning sentence is rendered");
assert.strictEqual(body.textContent, "«i18n.badge_body»", "from the keyed string");
var more = find(note, "i18n-badge-link");
assert.ok(more, "the first link exists");
assert.strictEqual(String(more.href), "#/help/translation-limitations",
  "details link points at the limitations article");
assert.ok(more.style.minHeight === "44px", "links meet the touch floor too");
var links = find(note, "i18n-badge-links");
assert.strictEqual(links.children.length, 2, "two links: what this means, and how to help");
var improve = links.children[1];
assert.ok(String(improve.href).indexOf("issues/new?labels=translation") !== -1,
  "the correction route is the labelled GitHub issues form");
assert.strictEqual(improve.target, "_blank", "it opens in a new tab");
assert.strictEqual(improve.rel, "noopener noreferrer", "without handing the opener over");

/* --- 3. the disclosure toggles through the SHARED delegated listener --- */
assert.strictEqual(clickListeners.length, 1, "one delegated click listener for the whole app");
click(chip);
assert.strictEqual(chip.getAttribute("aria-expanded"), "true", "first tap expands");
assert.strictEqual(note.hidden, false, "first tap reveals the note");
click(chip);
assert.strictEqual(chip.getAttribute("aria-expanded"), "false", "second tap collapses");
assert.strictEqual(note.hidden, true, "second tap hides the note again");
click(chip);
assert.strictEqual(note.hidden, false, "the disclosure cycles, it is not a one-shot");
click(chip);
assert.ok(host.children.indexOf(chip) === 0 && host.children.indexOf(note) === 1,
  "collapsing never removes the chip or the note from the slot — the warning is not dismissible");

/* --- 4. a locale change re-decides without re-mounting ------------------ */
localeCode = "en";
B.refresh();
assert.strictEqual(host.children.length, 0, "switching back to English empties the slot");
assert.strictEqual(B.visible(), false, "and visible() follows");
localeCode = "es";
B.refresh();
assert.strictEqual(host.children.length, 2, "switching to a machine dict paints it again");
assert.strictEqual(B.visible(), true, "visible() follows the locale both ways");

/* --- 5. two chips do not share an id or a state ------------------------ */
var host2 = el("div");
hosts.host2 = host2;
B.mount(document, host2);
var chip2 = host2.children[0];
var note2 = host2.children[1];
assert.notStrictEqual(chip2.getAttribute("aria-controls"), note.id,
  "each mount gets its own panel id — aria-controls never points at a stale one");
click(chip);
assert.strictEqual(note.hidden, true, "the first chip was collapsed, so it stays collapsed");
click(chip2);
assert.strictEqual(note2.hidden, false, "opening the second note leaves the first closed");
click(chip2);

/* --- 6. the warning is never persisted --------------------------------- */
assert.deepStrictEqual(storageCalls, [],
  "no storage read or write, ever: a warning the user can lose is not a warning");

/* --- 7. degraded harnesses (the module header claims "never throws") ---- */
/* (a) no I18n at all — the chip cannot know the locale, so it stays silent. */
var noI18n = { document: document, localStorage: localStorage };
noI18n.window = noI18n;
vm.createContext(noI18n);
vm.runInContext(load("vanilla/js/ui/i18n-badge.js"), noI18n);
var host3 = el("div");
hosts.host3 = host3;
assert.doesNotThrow(function () { noI18n.I18nBadge.mount(document, host3); },
  "no I18n must not throw out of the header");
assert.strictEqual(host3.children.length, 0, "no I18n means no chip (never a false warning)");
assert.strictEqual(noI18n.I18nBadge.visible(), false, "visible() is false without I18n");
assert.doesNotThrow(function () { noI18n.I18nBadge.refresh(); }, "refresh without I18n is a no-op");

/* (b) I18n present but incomplete, and (c) a throwing locale(): every one of
 * them must degrade to silence — the badge may only appear on a positive
 * proof, never on an error path. */
function probe(label, i18n) {
  var box = { document: document, localStorage: localStorage };
  if (i18n) box.I18n = i18n;
  box.window = box;
  vm.createContext(box);
  vm.runInContext(load("vanilla/js/ui/i18n-badge.js"), box);
  var target = el("div");
  box.mountTarget = target;
  box.I18nBadge.mount(document, target);
  assert.strictEqual(target.children.length, 0, label + " renders no chip");
  assert.strictEqual(box.I18nBadge.visible(), false, label + " reports nothing visible");
}
probe("an I18n without isMachineLocale", { locale: function () { return "es"; } });
probe("an I18n whose locale() throws", {
  locale: function () { throw new Error("registry exploded"); },
  isMachineLocale: function () { return true; }
});
probe("an I18n whose isMachineLocale throws", {
  locale: function () { return "es"; },
  isMachineLocale: function () { throw new Error("registry exploded"); }
});
probe("an I18n whose locale() answers a non-string", {
  locale: function () { return 42; },
  isMachineLocale: function () { return true; }
});
probe("an I18n whose locale() answers nothing", {
  locale: function () { return ""; },
  isMachineLocale: function () { return true; }
});

/* (d) no DOM global (utils/dom.js not loaded): the chip still renders from
 * the raw platform calls, because a header that throws is worse than one
 * without a chip. */
var noDom = { document: document, localStorage: localStorage, I18n: fakeI18n() };
noDom.window = noDom;
vm.createContext(noDom);
vm.runInContext(load("vanilla/js/utils/touchable.js"), noDom);
vm.runInContext(load("vanilla/js/utils/event.js"), noDom);
vm.runInContext(load("vanilla/js/ui/i18n-badge.js"), noDom);
var host4 = el("div");
localeCode = "es";
noDom.I18nBadge.mount(document, host4);
assert.strictEqual(host4.children.length, 2, "without the DOM helper the chip still renders");
assert.ok(find(host4, "i18n-badge"), "and it is still the chip class");

/* (e) no document at all, and (f) odd arguments: no throw, no chip. */
var headless = { localStorage: localStorage, I18n: fakeI18n() };
headless.window = headless;
vm.createContext(headless);
vm.runInContext(load("vanilla/js/utils/touchable.js"), headless);
vm.runInContext(load("vanilla/js/utils/dom.js"), headless);
vm.runInContext(load("vanilla/js/utils/event.js"), headless);
vm.runInContext(load("vanilla/js/ui/i18n-badge.js"), headless);
assert.doesNotThrow(function () { headless.I18nBadge.mount(undefined, undefined); },
  "mount(undefined, undefined) must not throw");
assert.strictEqual(headless.I18nBadge.visible(), false, "and must not claim to be visible");
assert.doesNotThrow(function () { headless.I18nBadge.refresh(); }, "refresh before mount is a no-op");
assert.strictEqual(headless.I18nBadge.visible(), false, "and still reports nothing visible");

/* --- 8. the CSS the JS promises: tokens, no hover-only UI, no motion ---- */
var css = load("vanilla/css/app.css");
var badgeCss = css.slice(css.indexOf("/* i18n honesty chip"));
assert.ok(badgeCss.length > 200, "app.css carries the badge rules");
assert.ok(!/#[0-9a-fA-F]{3,8}\b/.test(badgeCss),
  "the badge paints from theme tokens only — no raw HEX that would break the other two themes");
assert.ok(/\.i18n-badge[^{]*\{[^}]*min-height:\s*44px/.test(badgeCss),
  "the chip's 44px touch floor is declared in CSS too, so it survives a page that skips touchable()");
assert.ok(/\.i18n-badge\[aria-expanded="true"\]/.test(badgeCss),
  "the expanded chip is visibly marked from aria-expanded — the same attribute AT reads, never a private flag");
assert.ok(/@media\s*\(prefers-reduced-motion:\s*reduce\)/.test(badgeCss)
  && /prefers-reduced-motion[\s\S]*?\.i18n-badge/.test(badgeCss),
  "the badge's only motion is silenced under prefers-reduced-motion");
assert.ok(badgeCss.indexOf(":hover") !== -1
  ? /\.i18n-badge-note[^{]*\{[^}]*:hover/.test(badgeCss) === false : true,
  "no hover-only affordance on the note — everything it offers is reachable by tap");

console.log("OK: i18n-badge");