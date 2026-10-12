/* confirm-risk-test: the signing dialog is shared by ALL operations, so it is
 * the single place a high-risk string gets its English reference. This test
 * pins the contract Task 4 added to ConfirmDialog.show:
 *
 *   - cfg.titleKey (optional) and rows[i][3] (optional termKey) drive
 *     RiskText.render, so a machine-filled locale can disclose the en master
 *     beside the line the user is about to sign.
 *   - ABSENT keys render exactly as before — that is what keeps the other
 *     ConfirmDialog.show call sites working untouched until they opt in.
 *   - The SEMANTIC elements survive: the title is still an <h3> and the row
 *     terms are still <dt>s inside the <dl>. The brief's draft replaced them
 *     with RiskText's <span>/<div>, which silently un-pairs every <dl> and
 *     downgrades the dialog heading; sections 1 and 11 are the guards.
 *
 * Harness notes (both are LOADINGS, not fakes — see risk-text-test.js for the
 * same reasoning):
 *   1. utils/dom.js, utils/touchable.js, utils/event.js, ui/risk-text.js and
 *      ui/confirm.js are the SHIPPED modules, loaded as-is. Stubbing the
 *      widgets would hide exactly the wiring this test exists to pin.
 *   2. The fake element aggregates `textContent` across its children the way
 *      a real DOM element does. Without that, an assertion like
 *      "the heading still carries the title" could not tell a real DOM from
 *      this shim, and a host element whose text lives in a child would read
 *      as empty — a false failure, not a real one.
 *   3. The fake I18n mirrors i18n.js's shipped contract (i18n.js:84-109)
 *      strictly: locale() names the code, isMachineLocale(code) is
 *      provenance(code)==="machine" and therefore false for "en" and for
 *      anything that is not a non-empty string, and enFor(key) is undefined
 *      for a key nothing knows.
 * Anything richer than this is the browser probe's job (tooling/visual/). */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");
var vm = require("vm");

var ROOT = path.join(__dirname, "..");
function load(rel) { return fs.readFileSync(path.join(ROOT, rel), "utf8"); }

var passed = 0;
function ok(cond, msg) { assert.ok(cond, msg); passed += 1; }
function eq(a, b, msg) { assert.strictEqual(a, b, msg); passed += 1; }

var clickListeners = [];

/* Fake element with REAL textContent semantics: setting textContent clears
 * children, reading it concatenates them. That is what a browser does, and it
 * is what makes "the h3 still carries the title" a meaningful assertion when
 * the title now lives inside a child node. */
function el(tag) {
  var node = {
    tagName: String(tag).toUpperCase(), children: [], attrs: {}, style: {},
    className: "", id: "", parentNode: null,
    setAttribute: function (k, v) { this.attrs[k] = String(v); },
    getAttribute: function (k) {
      return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
    },
    hasAttribute: function (k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); },
    removeAttribute: function (k) { delete this.attrs[k]; },
    appendChild: function (c) { if (c) c.parentNode = this; this.children.push(c); return c; },
    insertBefore: function (c, ref) {
      var i = this.children.indexOf(ref);
      if (i === -1) this.children.push(c); else this.children.splice(i, 0, c);
      if (c) c.parentNode = this;
      return c;
    },
    addEventListener: function () {}
  };
  var ownText = "";
  var hiddenFlag = false;
  /* `type` reflects to attributes the way real elements do, so
   * getAttribute("type") and .type cannot disagree — risk-text.js sets the
   * asterisk's type as a plain property, and the harness must see both. */
  Object.defineProperty(node, "type", {
    get: function () { return this.attrs.type === undefined ? "" : this.attrs.type; },
    set: function (v) { this.attrs.type = String(v); }
  });
  Object.defineProperty(node, "textContent", {
    get: function () {
      if (!this.children.length) return ownText;
      return this.children.map(function (c) {
        return (c && c.textContent !== undefined && c.textContent !== null) ? String(c.textContent) : "";
      }).join("");
    },
    set: function (v) {
      ownText = (v === undefined || v === null) ? "" : String(v);
      this.children.length = 0;
    }
  });
  Object.defineProperty(node, "hidden", {
    get: function () { return hiddenFlag; },
    set: function (v) { hiddenFlag = !!v; if (v) { this.attrs.hidden = ""; } else { delete this.attrs.hidden; } }
  });
  return node;
}

function makeDoc() {
  var handlers = {};
  return {
    __handlers: handlers,
    createElement: el,
    addEventListener: function (t, fn) { if (t === "click") clickListeners.push(fn); else handlers[t] = fn; },
    removeEventListener: function (t, fn) {
      if (t !== "click") { delete handlers[t]; return; }
      var i = clickListeners.indexOf(fn);
      if (i !== -1) clickListeners.splice(i, 1);
    }
  };
}

var doc = makeDoc();

/* EN master for the keys this test drives. Values are the en.json master
 * strings, so "the panel shows the reference" means byte-for-byte the master,
 * not "contains the words". */
var EN = {
  "confirm.title": "Confirm transfer",
  "trade.co_orderid": "Order ID",
  "settings.th_node": "Node",
  "credit.uc_title": "Unlock to sign"
};
var localeCode = "es";
var machine = true;
var enForCalls = [];
function fakeI18n() {
  return {
    locale: function () { return localeCode; },
    /* strict, like the real provenance(): machine only for a non-empty
     * non-"en" code — a permissive fake would hide a caller that forgot to
     * pass the code at all. */
    isMachineLocale: function (code) {
      return machine && typeof code === "string" && !!code && code !== "en";
    },
    enFor: function (k) {
      enForCalls.push(k);
      return Object.prototype.hasOwnProperty.call(EN, k) ? EN[k] : undefined;
    }
  };
}

var sandbox = { document: doc, I18n: fakeI18n() };
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(load("vanilla/js/utils/touchable.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/dom.js"), sandbox);
vm.runInContext(load("vanilla/js/utils/event.js"), sandbox);
vm.runInContext(load("vanilla/js/ui/risk-text.js"), sandbox);
vm.runInContext(load("vanilla/js/ui/confirm.js"), sandbox);
var ConfirmDialog = sandbox.ConfirmDialog;

function findAll(root, tag) {
  var out = [];
  (function walk(n) {
    if (!n) return;
    if (String(n.tagName || "").toUpperCase() === tag) out.push(n);
    (n.children || []).forEach(walk);
  })(root);
  return out;
}
function findCls(root, cls) {
  var out = [];
  (function walk(n) {
    if (!n) return;
    if (String(n.className || "").split(/\s+/).indexOf(cls) !== -1) out.push(n);
    (n.children || []).forEach(walk);
  })(root);
  return out;
}
function kids(node) { return node.children || []; }

/* ------------------------------------------------------------------ *
 * 1. BACKWARDS COMPATIBILITY. A dialog with no keys anywhere must render
 *    exactly what it rendered before Task 4: an <h3>, a <dl class="confirm">
 *    of dt/dd pairs, the fee dt, and the actions row.
 * ------------------------------------------------------------------ */
enForCalls = [];
var box = ConfirmDialog.show({
  doc: doc,
  title: "Cancel order?",
  rows: [["Amount", "12.0 BTS"], ["Order ID", "1.7.42"]],
  onBack: function () {},
  onSend: function () {}
});
eq(kids(box).map(function (c) { return c.tagName; }).join(","), "H3,DL,DIV",
  "unkeyed dialog keeps h3 / dl / actions — the same three children as before");
var h3 = findAll(box, "H3")[0];
ok(h3, "the title is still an h3 element");
eq(h3.textContent, "Cancel order?", "the heading still carries the title text");
var dl = findAll(box, "DL")[0];
ok(String(dl.className).split(/\s+/).indexOf("confirm") !== -1, "dl.confirm survives");
var dts = findAll(dl, "DT"), dds = findAll(dl, "DD");
eq(dts.length, 2, "one dt per row");
eq(dds.length, 2, "one dd per row");
eq(dts[0].textContent, "Amount", "dt text is unchanged");
eq(dds[0].textContent, "12.0 BTS", "dd text is unchanged");
eq(enForCalls.length, 0, "an unkeyed dialog never asks for an English source");
ok(findCls(box, "i18n-risk").length === 0, "no disclosure markup on an unkeyed dialog");

/* ------------------------------------------------------------------ *
 * 2. A KEYED TITLE carries the English reference, inside the h3.
 * ------------------------------------------------------------------ */
var tbox = ConfirmDialog.show({
  doc: doc,
  title: "Confirmar la transferencia",
  titleKey: "confirm.title",
  rows: [],
  onBack: function () {},
  onSend: function () {}
});
var th3 = findAll(tbox, "H3")[0];
ok(th3, "the keyed title is still an h3");
var wrap = findCls(th3, "i18n-risk")[0];
ok(wrap, "the keyed title rendered the dual-line wrapper");
eq(findCls(th3, "i18n-risk-native")[0].textContent, "Confirmar la transferencia",
  "the user's language stays on the line the user reads");
eq(findCls(th3, "i18n-risk-en")[0].textContent, "Confirm transfer",
  "the disclosure is the en master string, byte-exact");
eq(findCls(th3, "i18n-risk-en")[0].hidden, true, "the English reference starts collapsed");
var star = findCls(th3, "i18n-risk-star")[0];
eq(star.tagName, "BUTTON", "the asterisk is a real button, not a hover-only span");
eq(star.getAttribute("aria-expanded"), "false", "disclosure starts collapsed");
eq(star.getAttribute("type"), "button", "the asterisk never submits a form");
ok(star.getAttribute("aria-controls"), "aria-controls names the panel");
eq(star.style.minHeight, "44px", "the shared 44px touch floor is applied");
var headText = th3.textContent;
ok(headText.indexOf("Confirmar la transferencia") !== -1, "the heading still carries the user's line");
ok(headText.indexOf("Confirm transfer") !== -1, "the heading carries the English reference too");
eq(headText.split("Confirmar la transferencia").length - 1, 1,
  "the user's line appears exactly once — nesting did not duplicate it beside the widget");
eq(headText.split("Confirm transfer").length - 1, 1,
  "the English reference appears exactly once — no panel doubled up");

/* ------------------------------------------------------------------ *
 * 3. PER-ROW GRANULARITY in ONE dialog: the keyed term dual-lines, the
 *    unkeyed dynamic value (an amount, an object id) stays plain.
 * ------------------------------------------------------------------ */
var mbox = ConfirmDialog.show({
  doc: doc,
  title: "Confirmar la transferencia",
  titleKey: "confirm.title",
  rows: [
    ["ID de orden", "1.7.42", null, "trade.co_orderid"],
    ["Cantidad", "1.234,56 BTS"]
  ],
  feeHuman: "0.10 BTS",
  feeTerm: "Comisión",
  onBack: function () {},
  onSend: function () {}
});
var mdl = findAll(mbox, "DL")[0];
var mdts = findAll(mdl, "DT"), mdds = findAll(mdl, "DD");
eq(mdts.length, 3, "two rows plus the fee line are all dt elements");
ok(findCls(mdts[0], "i18n-risk").length === 1, "the keyed term dual-lined");
eq(findCls(mdts[0], "i18n-risk-en")[0].textContent, "Order ID", "the keyed term's reference is its own en master");
ok(findCls(mdts[1], "i18n-risk").length === 0, "the unkeyed term does not dual-line");
eq(mdts[1].textContent, "Cantidad", "the unkeyed term still reads as written");
eq(mdts[1].tagName, "DT", "and it is still a <dt>, so the <dl> pairing survives");
ok(findCls(mdds[0], "i18n-risk").length === 0, "a VALUE is never wrapped — amounts/ids are locale-independent (§3.5)");
eq(mdds[0].textContent, "1.7.42", "the id reads verbatim");
eq(mdds[1].textContent, "1.234,56 BTS", "the amount reads verbatim");

/* ------------------------------------------------------------------ *
 * 4. rows[i][3] IS the key slot; rows[i][2] is still the raw title
 *    (principle #6: human terms, raw behind the tooltip).
 * ------------------------------------------------------------------ */
var rbox = ConfirmDialog.show({
  doc: doc,
  title: "x",
  rows: [["Nota", "hola", "raw-999", "trade.co_orderid"]],
  onBack: function () {},
  onSend: function () {}
});
var rdl = findAll(rbox, "DL")[0];
eq(findAll(rdl, "DD")[0].title, "raw-999", "the third element still sets dd.title");
eq(findAll(rdl, "DT")[0].tagName, "DT", "the fourth element did not displace the dt");
ok(findCls(rdl, "i18n-risk").length === 1, "the fourth element is consumed as the term key");
eq(findCls(rdl, "i18n-risk-en")[0].textContent, "Order ID", "and drives the reference");

/* ------------------------------------------------------------------ *
 * 5. ONE English lookup per dual-line line, and none for the rest — the
 *    dialog must not ask for a reference it will not show.
 * ------------------------------------------------------------------ */
enForCalls = [];
ConfirmDialog.show({
  doc: doc,
  title: "Confirmar la transferencia",
  titleKey: "confirm.title",
  rows: [["ID de orden", "1.7.42", null, "trade.co_orderid"], ["Cantidad", "1 BTS"]],
  onBack: function () {},
  onSend: function () {}
});
eq(enForCalls.join(","), "confirm.title,trade.co_orderid",
  "exactly the keyed strings are looked up, once each, in render order");

/* ------------------------------------------------------------------ *
 * 6. THE DECISION IS NOT CONFIRMDIALOG'S. Flip the two things RiskText
 *    decides on — the active locale and whether the text already IS the
 *    English — and the same keys render plain.
 * ------------------------------------------------------------------ */
localeCode = "en";
var ebox = ConfirmDialog.show({
  doc: doc,
  title: "Confirmar la transferencia",
  titleKey: "confirm.title",
  rows: [["ID de orden", "1.7.42", null, "trade.co_orderid"]],
  onBack: function () {},
  onSend: function () {}
});
ok(findCls(ebox, "i18n-risk").length === 0, "under en nothing dual-lines (the caller passed a code-less locale)");
eq(findAll(ebox, "H3")[0].textContent, "Confirmar la transferencia", "and the text is untouched");

machine = false;
localeCode = "es";
var vbox = ConfirmDialog.show({
  doc: doc,
  title: "Confirmar la transferencia",
  titleKey: "confirm.title",
  rows: [["ID de orden", "1.7.42", null, "trade.co_orderid"]],
  onBack: function () {},
  onSend: function () {}
});
ok(findCls(vbox, "i18n-risk").length === 0, "a human-reviewed locale loses every asterisk");
machine = true;
/* Text already IS the English -> nothing to disclose, even on es. */
var sbox = ConfirmDialog.show({
  doc: doc,
  title: "Confirm transfer",
  titleKey: "confirm.title",
  rows: [["Order ID", "1.7.42", null, "trade.co_orderid"]],
  onBack: function () {},
  onSend: function () {}
});
ok(findCls(sbox, "i18n-risk").length === 0, "no reference is invented when the line already reads as English");

/* ------------------------------------------------------------------ *
 * 7. DEGENERATE INPUT never throws and never loses the text. The dialog
 *    is the last gate before a signature, so a bad key degrades the line,
 *    never the dialog.
 * ------------------------------------------------------------------ */
var weird = [
  ["42", null], [null, "note"], ["", "note"], [{}, "note"], [true, "note"]
];
weird.forEach(function (pair, idx) {
  var wb = ConfirmDialog.show({
    doc: doc,
    title: "Title",
    titleKey: pair[0],
    rows: [["Term", "Value", null, pair[1]], ["Other", "V2", null, "nope.nobody.knows"]],
    onBack: function () {},
    onSend: function () {}
  });
  ok(wb, "dialog " + idx + " rendered with key " + JSON.stringify(pair[0]));
  var wdl = findAll(wb, "DL")[0], wdts = findAll(wdl, "DT");
  eq(wdts.length, 2, "dialog " + idx + " keeps both dt elements");
  eq(wdts[0].textContent, "Term", "dialog " + idx + " keeps the term text");
  eq(wdts[1].textContent, "Other", "dialog " + idx + " keeps the second term text");
});
ok(findCls(ConfirmDialog.show({ doc: doc, title: "T", rows: null, onBack: function () {}, onSend: function () {} }), "i18n-risk").length === 0,
  "absent rows render an empty dialog without throwing");

/* ------------------------------------------------------------------ *
 * 8. THE MODULE GUARD. A page that somehow did not load ui/risk-text.js
 *    must still get the whole dialog: this is the same fail-soft shape
 *    ui/confirm.js already uses for DOM and touchable.
 * ------------------------------------------------------------------ */
var bareDoc = makeDoc();
var bare = { document: bareDoc };
bare.window = bare;
vm.createContext(bare);
vm.runInContext(load("vanilla/js/utils/touchable.js"), bare);
vm.runInContext(load("vanilla/js/utils/dom.js"), bare);
vm.runInContext(load("vanilla/js/ui/confirm.js"), bare);
ok(typeof bare.RiskText === "undefined", "the bare sandbox really has no RiskText");
var bbox = bare.ConfirmDialog.show({
  doc: bareDoc,
  title: "Confirm transfer",
  titleKey: "confirm.title",
  rows: [["Order ID", "1.7.42", null, "trade.co_orderid"]],
  onBack: function () {},
  onSend: function () {}
});
var bdl = findAll(bbox, "DL")[0];
eq(findAll(bbox, "H3")[0].textContent, "Confirm transfer", "no RiskText: the heading still carries the title");
eq(findAll(bdl, "DT").length, 1, "no RiskText: the row term is still a dt");
eq(findAll(bdl, "DT")[0].textContent, "Order ID", "no RiskText: the term text survives");
eq(findAll(bdl, "DD")[0].textContent, "1.7.42", "no RiskText: the value survives");
ok(findCls(bbox, "i18n-risk").length === 0, "no RiskText: no disclosure markup, and no throw");

console.log("ConfirmDialog risk wiring: " + passed + " passed, 0 failed");