/* help-translation-limitations-test: the honesty article the header chip and
 * every *-marked signing line link to. It is the only place that tells a
 * reader what "machine-filled" means and how to get a string fixed, so the
 * things it PROMISES are checked here rather than trusted:
 *
 *   1. the article exists under the slug both honesty surfaces link to;
 *   2. its per-language confidence table matches the approved rating set
 *      (es/fr/de/it/pt high, ru/zh/ja/ko good, hi/tr moderate) — data pinned
 *      here AND in HelpUI._test.CONFIDENCE, so the table can never drift from
 *      the prose;
 *   3. the table renders on a WIDE screen and the same rows render as cards
 *      for phones: the shared .node-table contract hides tables under 560px
 *      (app.css:221), so a table-only implementation shows a phone reader
 *      nothing at all;
 *   4. the correction route is a real external link to the issue tracker with
 *      the translation label;
 *   5. the honesty surfaces point AT this article (reachability, AGENTS.md §7
 *      rule 10), and its keys exist in every shipped dictionary.
 *
 * Runs: node tooling/help-translation-limitations-test.js (exit 0 = green). */
"use strict";
var assert = require("assert");
var fs = require("fs");
var path = require("path");

var ROOT = path.join(__dirname, "..");
var SLUG = "translation-limitations";
var ARTICLE = "#/help/" + SLUG;
var ISSUES = "https://github.com/litepresence/bitshares-vanilla-ui/issues/new?labels=translation";

/* --- fake DOM: tag/.class/#id selectors, attribute store, no browser ----- */
function fakeEl(tag) {
  var el = { tag: tag, children: [], attrs: {}, style: {}, text: "",
    className: "", parentNode: null, firstChild: null, clicks: {} };
  /* Real DOM aggregates textContent from child nodes, and setting it replaces
   * them. Modelling that is what lets the card assertions read a card's text
   * without walking it — and it is why a widget that builds its content as
   * children (instead of stuffing one string into textContent) cannot pass. */
  Object.defineProperty(el, "textContent", {
    get: function () {
      if (this.children.length) {
        return this.children.map(function (c) { return c.textContent; }).join("");
      }
      return this.text;
    },
    set: function (v) { this.text = String(v); this.children = []; this.firstChild = null; }
  });
  el.setAttribute = function (k, v) { this.attrs[k] = String(v); };
  el.getAttribute = function (k) {
    return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null;
  };
  el.hasAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); };
  el.removeAttribute = function (k) { delete this.attrs[k]; };
  el.appendChild = function (c) { if (!c) return c; c.parentNode = el; this.children.push(c); this.firstChild = this.children[0] || null; return c; };
  el.insertBefore = function (c, ref) {
    c.parentNode = el;
    var i = this.children.indexOf(ref);
    if (i === -1) this.children.push(c); else this.children.splice(i, 0, c);
    this.firstChild = this.children[0] || null;
    return c;
  };
  el.removeChild = function (c) {
    var i = this.children.indexOf(c);
    if (i !== -1) this.children.splice(i, 1);
    this.firstChild = this.children[0] || null;
    return c;
  };
  el.addEventListener = function (t, f) { this.clicks[t] = f; };
  el.classList = { add: function (c) { el.className = (el.className + " " + c).trim(); } };
  /* Real elements reflect target/rel properties onto attributes (and back), so
   * getAttribute("target") sees what the code assigned. Modelling that keeps
   * the harness honest whichever way the view writes the link. */
  ["target", "rel", "href"].forEach(function (name) {
    Object.defineProperty(el, name, {
      get: function () { return this.getAttribute(name); },
      set: function (v) { this.setAttribute(name, v); }
    });
  });
  function classes(n) { return String(n.className || "").split(/\s+/); }
  function matches(n, sel) {
    if (sel.charAt(0) === "#") return n.getAttribute("id") === sel.slice(1);
    if (sel.charAt(0) === ".") return classes(n).indexOf(sel.slice(1)) !== -1;
    return n.tag === sel;
  }
  function walk(n, sel, out) {
    for (var i = 0; i < n.children.length; i++) {
      if (matches(n.children[i], sel)) out.push(n.children[i]);
      walk(n.children[i], sel, out);
    }
    return out;
  }
  el.querySelectorAll = function (sel) {
    var out = [];
    String(sel).split(",").forEach(function (s) { walk(el, s.trim(), out); });
    return out;
  };
  el.querySelector = function (sel) { return el.querySelectorAll(sel)[0] || null; };
  return el;
}
function fakeDoc() {
  return { createElement: fakeEl, createTextNode: function (s) {
    var n = fakeEl("#text"); n.textContent = String(s); return n; } };
}

/* --- load the SHIPPED modules, not stubs: the article's table goes through
 *     the shared TableRenderer and its strings through the real t(), so a stub
 *     would hide exactly the wiring under test. ----------------------------- */
var I18n = require("../vanilla/js/i18n.js");
global.I18n = I18n;
global.DOM = require("../vanilla/js/utils/dom.js");
global.TableRenderer = require("../vanilla/js/ui/table.js");
var enDict = JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales/en.json"), "utf8"));
I18n._seed("en", enDict);
I18n._setCurrent("en");
var HelpUI = require("../vanilla/js/views/help-ui.js");

function render() {
  var doc = fakeDoc();
  /* TableRenderer.render() reads the global document (as every view's table
   * does); the root's ownerDocument is what the rest of the article uses. */
  global.document = doc;
  var root = fakeEl("div");
  root.ownerDocument = doc;
  HelpUI.renderHelp(root, { wildcard: SLUG });
  return root;
}

var passed = 0;
function ok(c, n) { assert.ok(c, n); passed++; }
function eq(a, e, n) { assert.strictEqual(a, e, n + " (got " + JSON.stringify(a) + ")"); passed++; }

/* --- 1. the article exists under the slug both surfaces link to ---------- */
var topic = HelpUI.TOPICS.filter(function (t) { return t[0] === SLUG; })[0];
ok(!!topic, "TOPICS carries the " + SLUG + " article");
eq(topic[1], "Translation limitations", "topic title matches en.json");
eq(I18n.t("help.topic_" + SLUG + "_title", ""), topic[1],
  "the topic title resolves from the locale dictionary");
var body = HelpUI._test.topicBody(SLUG);
ok(body.length > 400, "the article has a real body (" + body.length + " chars)");
/* topicBody() is the code-side fallback (blocks joined by "\n"); the shipped
 * dictionary value is the string the page actually renders, and paintBody
 * splits it on blank lines. Both must open with the same caveat paragraph —
 * 65 of the 68 shipped articles are byte-identical this way, and a body that
 * drifts between the two is a silent fork (check_i18n cannot see it: the
 * help-topic t() key is built at runtime, so no literal default is compared). */
var codeBlocks = String(body).split("\n");
var dictBody = String(enDict.help["topic_" + SLUG + "_body"]);
var dictBlocks = dictBody.split(/\n\s*\n/);
eq(dictBlocks[0], codeBlocks[0], "the caveat paragraph is the first block in code and dictionary");
eq(dictBlocks.join("\n"), codeBlocks.join("\n"),
  "the dictionary body and the code fallback are the same article");
ok(codeBlocks[0].indexOf("# ") !== 0, "the article opens on prose, not a heading");
ok(/machine/i.test(codeBlocks[0]), "the caveat says the wording was machine-written");

/* The promises the chip and the * lines make, in the article's own words. */
ok(/machine/i.test(body), "the article says the wording was machine-written");
ok(/nobody|no person|has not been|no human/i.test(body), "and that no human has checked it");
ok(body.indexOf("*") !== -1, "the article explains the * marker");
ok(/english/i.test(body), "and that the English reference is reachable");
var headings = String(body).split(/\n(?=# )/).map(function (h) { return h.split("\n")[0]; });
ok(headings.length >= 4, "the article is sectioned (" + headings.length + " sections)");

/* --- 2. the confidence data is the approved rating set, in ONE place ----- */
var CONFIDENCE = HelpUI._test.CONFIDENCE;
var SPEC = {
  es: "high", fr: "high", de: "high", it: "high", pt: "high",
  ru: "good", zh: "good", ja: "good", ko: "good",
  hi: "moderate", tr: "moderate"
};
eq(CONFIDENCE.length, Object.keys(SPEC).length,
  "one rating per machine-filled language shipped (English is the reference, not a row)");
var dataByCode = {};
CONFIDENCE.forEach(function (r) {
  eq(r.length, 2, "a rating row is [locale, level]");
  assert.ok(!dataByCode[r[0]], "one rating per locale: " + r[0]);
  dataByCode[r[0]] = r[1];
});
Object.keys(SPEC).forEach(function (code) {
  eq(dataByCode[code], SPEC[code], "confidence for " + code);
});
eq(dataByCode.en, undefined, "English carries no rating — it is the reference text");
/* "One data place" is enforced, not just intended: the prose must not name a
 * specific language, or a second copy of the table would live in text that no
 * test reads and every translator has to keep in step by hand. The scan looks
 * for endonyms (Español, Deutsch, …) rather than locale codes: two-letter codes
 * like "it" or "es" collide with ordinary English words in the prose, so a
 * code scan would either cry wolf or force the article into wordless phrasing. */
var endonymTable = I18n.names();
var endonyms = Object.keys(endonymTable)
  .filter(function (code) { return code !== "en"; })   /* English is the reference, not a rated row */
  .map(function (code) { return endonymTable[code]; });
var namedInProse = endonyms.filter(function (name) {
  return String(body).indexOf(name) !== -1;
});
assert.deepStrictEqual(namedInProse, [],
  "the prose names no specific language (only CONFIDENCE + I18n.names do): " + namedInProse.join(", "));

/* --- 3. both surfaces of the table render the SAME rows ------------------- */
var root = render();
var wrap = root.querySelector(".wrap");
ok(!!wrap, "the article rendered a wrap");
var table = wrap.querySelector("table");
ok(!!table, "the confidence table is a real <table>");
ok(table.className.split(/\s+/).indexOf("node-table") !== -1,
  "it carries the shared .node-table class (striping, sticky first column)");
var ths = table.querySelectorAll("th");
eq(ths.length, 2, "the table has two columns");
eq(ths[0].textContent, I18n.t("help.confidence_language", ""), "column 1 is the language");
eq(ths[1].textContent, I18n.t("help.confidence_level", ""), "column 2 is the confidence");
var bodyRows = table.querySelectorAll("tbody")[0].querySelectorAll("tr");
eq(bodyRows.length, CONFIDENCE.length, "one table row per rated language");
var names = I18n.names();
bodyRows.forEach(function (tr, i) {
  var tds = tr.querySelectorAll("td");
  eq(tds.length, 2, "row " + i + " has two cells");
  eq(tds[0].textContent, names[CONFIDENCE[i][0]],
    "row " + i + " names " + CONFIDENCE[i][0] + " in its own language");
  eq(tds[1].textContent, I18n.t("help.confidence_" + CONFIDENCE[i][1], ""),
    "row " + i + " shows the " + CONFIDENCE[i][1] + " label");
});
var cards = wrap.querySelector(".node-cards");
ok(!!cards, "the phone card list exists (the table is hidden under 560px)");
var cardEls = cards.querySelectorAll(".node-card");
eq(cardEls.length, CONFIDENCE.length, "one card per rated language");
cardEls.forEach(function (card, i) {
  var txt = card.textContent;
  ok(String(txt).indexOf(names[CONFIDENCE[i][0]]) !== -1, "card " + i + " names its language");
  ok(String(txt).indexOf(I18n.t("help.confidence_" + CONFIDENCE[i][1], "")) !== -1,
    "card " + i + " shows its rating — never a blank card");
});

/* --- 4. the correction route is a real, labelled, external link ---------- */
var links = wrap.querySelectorAll("a").filter(function (a) {
  return String(a.getAttribute("href") || "").indexOf("github.com") !== -1;
});
eq(links.length, 1, "exactly one link to the issue tracker");
eq(links[0].getAttribute("href"), ISSUES, "it opens a pre-labelled translation issue");
eq(links[0].getAttribute("target"), "_blank", "external link opens in a new tab");
ok(/noopener/.test(String(links[0].getAttribute("rel") || "")), "with rel=noopener");
ok(String(links[0].textContent).length > 0, "the link has a label");

/* --- 5. reachable: the honesty surfaces point at this article, and the
 *        dictionary carries every key the article and the widget use. ------ */
["vanilla/js/ui/i18n-badge.js", "vanilla/js/ui/risk-text.js"].forEach(function (rel) {
  ok(fs.readFileSync(path.join(ROOT, rel), "utf8").indexOf(ARTICLE) !== -1,
    rel + " links to the article");
});
var KEYS = [
  "help.topic_" + SLUG + "_title", "help.topic_" + SLUG + "_text", "help.topic_" + SLUG + "_body",
  "help.translation_confidence_heading", "help.confidence_language", "help.confidence_level",
  "help.confidence_high", "help.confidence_good", "help.confidence_moderate",
  "help.report_translation_link",
  "i18n.risk_show_english", "i18n.risk_about_translations"
];
function flat(d, p) {
  var out = {};
  p = p || "";
  Object.keys(d).forEach(function (k) {
    if (k === "_meta") return;
    if (d[k] && typeof d[k] === "object") Object.assign(out, flat(d[k], p + k + "."));
    else out[p + k] = d[k];
  });
  return out;
}
var dicts = fs.readdirSync(path.join(ROOT, "vanilla/locales")).filter(function (f) {
  return /\.json$/.test(f);
});
eq(dicts.length, 12, "12 locale dictionaries ship");
var enFlat = flat(enDict);
dicts.forEach(function (f) {
  var flatDict = flat(JSON.parse(fs.readFileSync(path.join(ROOT, "vanilla/locales", f), "utf8")));
  KEYS.forEach(function (k) {
    ok(typeof flatDict[k] === "string" && flatDict[k].length > 0,
      f + " carries " + k);
    ok(flatDict[k] === enFlat[k],
      f + " keeps " + k + " an honest English stub until a human verifies it");
  });
});

/* --- 6. degradation: no shared table renderer, no blank article ---------- */
var realTable = global.TableRenderer;
global.TableRenderer = undefined;
try {
  var bare = render();
  var bareWrap = bare.querySelector(".wrap");
  var bareCards = bareWrap.querySelector(".node-cards");
  ok(!!bareCards, "without TableRenderer the card list still renders");
  eq(bareCards.querySelectorAll(".node-card").length, CONFIDENCE.length,
    "every language is still listed — the information is never dropped");
} finally {
  global.TableRenderer = realTable;
}

console.log("help-translation-limitations: " + passed + " passed");
