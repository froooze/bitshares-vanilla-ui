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

/* --- 1b. the FOUR promises, each pinned to content, not to a heading count --
 * The first version of this file only checked that /machine/i, the *, /english/i
 * and four headings were present. Deleting the whole "Corrections are the only
 * path to human reviewed" section — from help-ui.js AND from all 12 dicts,
 * consistently, so even check_i18n stays green — left every gate passing: an
 * article that promised nothing about how to fix a line, and told the reader
 * that no promise existed. These assertions read the SENTENCES, so each
 * removal of one of the four promises turns one of them red.
 */
function sectionBody(name) {
  var at = String(body).indexOf(name);
  if (at === -1) return "";
  return String(body).slice(at).split(/\n(?=# )/)[0];
}
/* (a) what "machine-filled" means — nobody has read it. */
ok(/nobody|no person|has not been|no human/i.test(String(body).split(/\n(?=# )/)[0]),
  "the opening paragraph, not just some paragraph, says no human has checked it");
/* (b) what the * means, and that the English is one tap away. */
var starSection = sectionBody("# What the * on a line means");
ok(starSection.length > 0, "the * has its own section");
ok(/english/i.test(starSection), "the * section says the English is reachable");
/* (c) how to correct a string — the section must survive as CONTENT, not as a
 * heading: a bare "# How to correct a string" with its instructions deleted is
 * exactly the regression this pins. */
var fixSection = sectionBody("# How to correct a string");
ok(fixSection.length > 0, "the article still has a 'How to correct a string' section");
ok(/report/i.test(fixSection), "that section tells the reader corrections start with a report");
ok(/\bkey\b/i.test(fixSection), "and to give the key the line discloses");
ok(/one report per line|per line/i.test(fixSection), "and how to shape the report");
ok(/link/i.test(fixSection), "and points at the pre-labelled link it renders below");
/* (d) corrections are the ONLY route to human reviewed — the promise that was
 * ungated. Both the heading and the sentence it carries are required: the
 * heading alone is what the old gate was reading. */
var humanSection = sectionBody("# Corrections are the only path to human reviewed");
ok(humanSection.length > 0, "the article still says corrections are the only path to human reviewed");
ok(/nothing else|only way|only path/i.test(humanSection),
  "and says so in words, not only in a heading");
ok(/person|human/i.test(humanSection), "and names a person reading the string as what flips it");

/* --- 1c. the * claim is re-derived from the shipped rule, not believed ------
 * The first version asserted something FALSE about the marker: "Amounts, object
 * ids, asset symbols and prices never carry a *". The shipped rule (i18n/
 * risk-keys.js) keys off SECTION and English wording, so starred lines embed
 * ids and amounts all over the dictionary. A false claim in the honesty
 * article is the worst bug it can ship, so the claim is checked against the
 * rule and the shipped en.json here, and each fact the prose leans on is
 * proved from the data. */
var RiskKeys = require("../vanilla/js/i18n/risk-keys.js");
var enFlat = flat(enDict);
var starred = RiskKeys.listFor(enFlat, enFlat);
var ID_RE = /\b1\.[0-9]+\.[0-9]+/;
var highRiskSections = Object.keys(RiskKeys.HIGH_RISK_SECTIONS);
/* Fact 1: starred lines DO carry ids and amounts — the old claim was wrong. */
var starredWithId = starred.filter(function (k) { return ID_RE.test(enFlat[k]); });
ok(starredWithId.length > 0,
  "the shipped rule stars lines that embed an object id (" + starredWithId.length + " do, e.g. " +
  starredWithId[0] + ") — so the article may not claim ids never carry a *");
var starredWithAmount = starred.filter(function (k) {
  return /\b\d[\d,]*\.\d+\b|\b\d+\s*(?:BTS|[A-Z]{3,10})\b/.test(enFlat[k]);
});
ok(starredWithAmount.length > 0,
  "and lines that embed an amount (" + starredWithAmount.length + " do, e.g. " +
  starredWithAmount[0] + ")");
/* Fact 2: "every line in a high-risk section" is also false on its own — the
 * rule carries a length cap, so a long high-risk line is deliberately not
 * starred. The article must therefore say "up to a length cap". */
var cappedOut = Object.keys(enFlat).filter(function (k) {
  return highRiskSections.indexOf(k.split(".")[0]) !== -1 &&
    enFlat[k].length > RiskKeys.MAX_RISK_LEN && !RiskKeys.isHighRisk(k, enFlat[k]);
});
ok(cappedOut.length > 0,
  "high-risk lines over the length cap are deliberately not starred (" + cappedOut.length + "), " +
  "so the article must not claim every high-risk line carries a *");
/* Fact 3: the one part of the old claim that IS true — a bare chain value is
 * not a translated line at all, so it cannot be starred. Proved by there being
 * no locale key that is nothing but digits and separators. */
var bareValues = Object.keys(enFlat).filter(function (k) {
  return /^[\s\d.,:%+-]*$/.test(String(enFlat[k])) && String(enFlat[k]).trim() !== "";
});
eq(bareValues.length, 0,
  "no locale string is a bare number — amounts and ids in cells are chain data, not lines");
/* Now the prose: the false prohibition is gone, and the three true statements
 * it leans on are present. */
ok(!/never carry a\s*\*/i.test(String(body)),
  "the article no longer claims ids/amounts never carry a *");
ok(/follows the line, not the words inside it|marker follows the line/i.test(String(body)),
  "it states the marker follows the line, not the content");
ok(/length cap/i.test(String(body)),
  "it states the length cap, because the rule has one");
ok(!/never carry a \*|Amounts, object ids, asset symbols and prices never/i.test(String(body)),
  "the old false sentence is gone from the article");

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
