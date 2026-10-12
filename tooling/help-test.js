/* help-test.js — help index invariants (menu-sitemap slice).
 * Stdlib only: `node tooling/help-test.js` (exit 0 = green). No DOM, no network.
 */
"use strict";
var assert = require("assert");
global.I18n = { t: function (k, d) { return d; } };
var HelpUI = require("../vanilla/js/views/help-ui.js");
var passed = 0;
function eq(a, e, n) { assert.strictEqual(a, e, n + " (got " + JSON.stringify(a) + ")"); passed++; }
function ok(c, n) { assert.ok(c, n); passed++; }
var T = HelpUI.TOPICS;
eq(T.length, 68, "68 topics");
var keys = T.map(function (r) { return r[0]; });
eq(new Set(keys).size, keys.length, "topic keys unique");
keys.forEach(function (k) {
  ok(HelpUI._test.topicBody(k).length > 0, "body for " + k);
});
var grouped = [];
HelpUI._test.GROUPS.forEach(function (g) {
  g[2].forEach(function (k) { grouped.push(k); });
});
eq(grouped.length, keys.length, "groups cover every topic exactly once");
eq(new Set(grouped).size, grouped.length, "no topic in two groups");
keys.forEach(function (k) {
  ok(grouped.indexOf(k) !== -1, k + " grouped");
});
["samet", "barter", "spotlight", "direct-debit", "api-lab", "es-lab",
  "charts", "dashboard", "register", "password", "news", "uris", "browser"].forEach(function (k) {
  ok(keys.indexOf(k) !== -1, "new topic " + k);
});
ok(keys.indexOf("sitemap") !== -1, "sitemap topic exists");

/* splitLinks: inline [label](#/hash) tokenizer (sitemap sitemap links). */
(function () {
  var split = HelpUI._test.splitLinks;
  ok(typeof split === "function", "splitLinks exported");
  if (typeof split !== "function") return;
  function deq(got, want, name) {
    assert.deepStrictEqual(got, want, name + " (got " + JSON.stringify(got) + ")");
    passed++;
  }
  deq(split("a [B](#/b) c "), [{ t: "text", s: "a " }, { t: "link", label: "B", href: "#/b" }, { t: "text", s: " c " }],
    "link tokenizes with surrounding text");
  deq(split("[X](https://evil.example.com)"), [{ t: "text", s: "[X](https://evil.example.com)" }],
    "external URL stays literal text (no off-app links from content)");
  deq(split("[](#/x)"), [{ t: "text", s: "[](#/x)" }], "empty label stays literal");
  deq(split("[X](#x)"), [{ t: "text", s: "[X](#x)" }], "non-route hash stays literal");
  deq(split("no links here"), [{ t: "text", s: "no links here" }], "plain text passes through");
  deq(split(""), [{ t: "text", s: "" }], "empty string yields one empty token");
  deq(split("[oops"), [{ t: "text", s: "[oops" }], "unbalanced bracket stays literal");
})();

/* Sitemap section nav: fake-doc render of #/help/sitemap — 9 buttons for
 * the 9 h2 markers, ids assigned, click scrolls + focuses, non-sitemap
 * topics get no nav. */
(function () {
  global.DOM = global.DOM || require("../vanilla/js/utils/dom.js");
  function fakeEl(tag) {
    var el = { tag: tag, children: [], parentNode: null, textContent: "",
      className: "", firstChild: null, scrolled: 0, focused: 0, clicks: {} };
    el.setAttribute = function (k, v) { el["attr_" + k] = String(v); };
    el.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(el, "attr_" + k) ? el["attr_" + k] : null; };
    el.appendChild = function (c) { c.parentNode = el; el.children.push(c); el.firstChild = el.children[0]; return c; };
    el.insertBefore = function (c, ref) {
      c.parentNode = el;
      var i = el.children.indexOf(ref);
      if (i === -1) el.children.push(c); else el.children.splice(i, 0, c);
      el.firstChild = el.children[0] || null;
      return c;
    };
    el.removeChild = function (c) {
      var i = el.children.indexOf(c);
      if (i !== -1) el.children.splice(i, 1);
      el.firstChild = el.children[0] || null;
      return c;
    };
    el.addEventListener = function (t, f) { el.clicks[t] = f; };
    el.classList = { add: function (c) { el.className = (el.className + " " + c).trim(); } };
    el.scrollIntoView = function () { el.scrolled++; };
    el.focus = function () { el.focused++; };
    el.contains = function (n) {
      if (n === el) return true;
      for (var i = 0; i < el.children.length; i++) if (el.children[i].contains(n)) return true;
      return false;
    };
    function match(n, sel) {
      if (sel.charAt(0) === "#") return n.getAttribute("id") === sel.slice(1);
      return n.tag === sel;
    }
    function walk(n, sel, out) {
      for (var i = 0; i < n.children.length; i++) {
        if (match(n.children[i], sel)) out.push(n.children[i]);
        walk(n.children[i], sel, out);
      }
      return out;
    }
    el.querySelectorAll = function (sel) {
      var parts = String(sel).split(",").map(function (s) { return s.trim(); });
      var out = [];
      parts.forEach(function (p) { walk(el, p, out); });
      return out;
    };
    el.querySelector = function (sel) { return el.querySelectorAll(sel)[0] || null; };
    return el;
  }
  var doc = {
    createElement: fakeEl,
    createTextNode: function (s) { var n = fakeEl("#text"); n.textContent = String(s); return n; }
  };
  function renderTopic(key) {
    var root = fakeEl("div");
    root.ownerDocument = doc;
    HelpUI.renderHelp(root, { wildcard: key });
    return root;
  }
  var sitemap = renderTopic("sitemap");
  var navs = sitemap.querySelectorAll("nav");
  eq(navs.length, 1, "sitemap renders one section nav");
  var btns = sitemap.querySelectorAll("button");
  eq(btns.length, 9, "nav holds 9 subsection buttons");
  var heads = sitemap.querySelectorAll("h2");
  eq(heads.length, 9, "article holds 9 section markers");
  var labels = btns.map(function (b) { return b.textContent; });
  var htexts = heads.map(function (h) { return (h.textContent || "").trim(); });
  assert.deepStrictEqual(labels, htexts, "button labels match headings in order (locale-proof)");
  passed++;
  heads.forEach(function (h, i) {
    eq(h.getAttribute("id"), "sitemap-sec-" + i, "marker id " + i);
    eq(h.getAttribute("tabindex"), "-1", "marker focusable " + i);
  });
  eq(navs[0].getAttribute("aria-label"), "Sections", "nav labeled for screen readers");
  ok(navs[0].className.split(" ").indexOf("help-sitemap-nav") !== -1, "nav carries the styling hook");
  btns.forEach(function (b) {
    ok(typeof b.clicks.click === "function", "button wires click (no hash change)");
  });
  btns[3].clicks.click();
  eq(heads[3].scrolled, 1, "click scrolls to its marker");
  eq(heads[3].focused, 1, "click moves focus to its marker");
  eq(heads[2].scrolled || 0, 0, "other markers untouched");
  var other = renderTopic("menu");
  eq(other.querySelectorAll("nav").length, 0, "non-sitemap topics get no nav");
  eq(other.querySelectorAll("button").length, 0, "non-sitemap topics get no buttons");
})();
(function () {
  global.Icon = undefined;
  var MenuUI = require("../vanilla/js/views/menu-ui.js");
  var hrefs = [];
  MenuUI.SECTIONS.forEach(function (s) { s.links.forEach(function (l) { hrefs.push(l.href); }); });
  var body = HelpUI._test.topicBody("sitemap");
  hrefs.forEach(function (h) {
    ok(body.indexOf("](#" + h.slice(1) + ")") !== -1 || body.indexOf("](" + h + ")") !== -1, "menu href in sitemap: " + h);
  });
  var fs = require("fs");
  var src = fs.readFileSync("/workspace/vanilla/js/router.js", "utf8");
  var patterns = [];
  var re = /path:\s*"([^"]+)"/g, m;
  while ((m = re.exec(src)) !== null) patterns.push(m[1]);
  ok(patterns.length > 40, "router patterns parsed (" + patterns.length + ")");
  function patToRx(p) {
    if (p === "*") return /^.*$/;
    var s = "^" + p.replace(/[.+?^${}()|[\]\\]/g, "\\$&")
      .replace(/\/\*\*/g, "(/.*)?").replace(/:[A-Za-z_]+/g, "[^/]+") + "$";
    return new RegExp(s);
  }
  var rxes = patterns.map(patToRx);
  var linkRe = /\]\((#[^)]+)\)/g, lm, bad = [];
  while ((lm = linkRe.exec(body)) !== null) {
    var path = lm[1].slice(1);
    var hit = rxes.some(function (rx) { return rx.test(path); });
    if (!hit) bad.push(lm[1]);
  }
  assert.deepStrictEqual(bad, [], "every sitemap link resolves to a route (" + patterns.length + " patterns)");
  passed++;
})();
console.log("help-test: " + passed + " passed");
