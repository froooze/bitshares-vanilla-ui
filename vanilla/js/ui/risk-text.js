/* ui/risk-text.js — the dual-line honesty surface for high-risk locale strings.
 * Owns: the one decision (dual-line vs plain, see dualEnglish), the asterisk
 *   disclosure button (real <button type="button">, aria-expanded +
 *   aria-controls, 44px touch floor — never a hover-only affordance, AGENTS.md
 *   §3.6), the English reference panel it toggles, and the link to the
 *   translation-limitations article from the exact line the user doubted.
 * Consumes: I18n.locale/isMachineLocale/enFor, DOM.el (element creation — never
 *   reimplemented here), the global touchable() (44px floor, same guard shape
 *   as ui/confirm.js so Node harnesses without it still render), EventDelegate
 *   (ONE delegated click listener, the shared helper — not a private one).
 * Side effects: creates detached elements; adds at most one delegated
 *   document-level "click" listener, on the first dual-line render only.
 *   No storage, no network, no signing.
 * Created by: building-vanilla-slices skill,
 *   docs/superpowers/plans/2026-10-12-i18n-machine-translation.md Task 3.
 * Failures: never throws. An unknown key, a missing English source (I18n.enFor
 *   returns undefined when the en master never loaded and no t() default was
 *   recorded), a non-machine locale, a verified locale, or a missing doc all
 *   degrade to the plain text wrapper — a missing reference beats a wrong one.
 *
 * Two UI strings below are still English literals (the asterisk's accessible
 * name and the article link's label). They cannot be keyed in this task: the
 * locale dictionaries and their _meta allowlists are not in this task's write
 * set, and an unkeyed t() call site fails the drift gate
 * (tooling/check_i18n.py). Task 6 adds the `i18n.risk_*` keys to all 12
 * dicts; these two literals are the exact strings reserved for them. */
var RiskText = (function () {
  "use strict";

  var ARTICLE = "#/help/translation-limitations";
  var EN_CLASS = "i18n-risk-en";
  var STAR_CLASS = "i18n-risk-star";
  var WRAP_CLASS = "i18n-risk";
  var OPEN_CLASS = "is-open";
  /* Reserved keys for the two literals above (Task 6 owns the dictionaries). */
  var SHOW_EN_LABEL = "Show the English reference for this line";
  var ABOUT_LABEL = "About these translations";

  var bound = false;
  var uid = 0;

  /* activeMachine: is the ACTIVE locale machine-filled and unverified?
   * I18n.isMachineLocale(code) takes the code (calling it bare answers
   * "not machine" for every locale — see i18n.js:107), so the code comes from
   * I18n.locale(). Failures: false when I18n is absent, incomplete, or
   * throws — a surface that cannot prove machine provenance must stay silent. */
  function activeMachine() {
    try {
      if (typeof I18n === "undefined" || !I18n || typeof I18n.isMachineLocale !== "function") return false;
      if (typeof I18n.locale !== "function") return false;
      var code = I18n.locale();
      if (typeof code !== "string" || !code) return false;
      return I18n.isMachineLocale(code) === true;
    } catch (e) {
      return false;
    }
  }

  /* englishSource: the English master text for a key, or null.
   * @param {string} key dotted locale key.
   * @returns {string|null} null when neither source knows the key.
   * Failure: never throws — a throwing enFor degrades to no reference. */
  function englishSource(key) {
    try {
      if (typeof I18n === "undefined" || !I18n || typeof I18n.enFor !== "function") return null;
      var src = I18n.enFor(key);
      return (typeof src === "string" && src) ? src : null;
    } catch (e) {
      return null;
    }
  }

  /* isVerified: has a human reviewed THIS key in the active locale?
   * SEAM — deliberately always false in this task. Task 5 reads the locale's
   * _meta.verified list (per-key human review) and answers true there, which
   * drops the asterisk from that line while leaving every unverified key of
   * the same machine-filled locale labelled. Kept as its own function so that
   * addition is one return statement, not a rewrite of dualEnglish.
   * @param {string} key dotted locale key (unused until Task 5 wires it).
   * @returns {boolean} always false today. */
  function isVerified(key) {
    return false;
  }

  /* mk: ONE element through the SHARED DOM helper — never reimplemented here.
   * Falls back to the raw owner.createElement only when the DOM global is
   * absent (a harness that did not load utils/dom.js), the same guard shape
   * ui/confirm.js uses, so a missing helper degrades the widget instead of
   * throwing a ReferenceError out of a signing dialog.
   * @param {Document} owner owner document (createElement known good — render
   *   resolves it before calling).
   * @param {string} tag tag name.
   * @param {string|null} text textContent; null leaves the element empty.
   * @param {string} [cls] optional className.
   * @returns {HTMLElement} new detached element. */
  function mk(owner, tag, text, cls) {
    if (typeof DOM !== "undefined" && DOM && typeof DOM.el === "function") {
      return DOM.el(owner, tag, text, cls);
    }
    var n = owner.createElement(tag);
    if (text !== undefined && text !== null) n.textContent = text;
    if (cls) n.className = cls;
    return n;
  }

  /* degraded: the no-document floor for render(). With no document there is
   * no element to build, but the answer must still NOT be null: Task 4 mounts
   * this straight into ConfirmDialog with appendChild, and appendChild(null)
   * inserts the visible text "null" into the dialog. An empty plain wrapper is
   * the honest floor — nothing is rendered rather than something wrong.
   * Unreachable in a page: every caller resolves a document first (and
   * ConfirmDialog.show throws "confirm: no document" without one). */
  function degraded() {
    return { className: "i18n-risk-plain", textContent: "", children: [] };
  }

  /* dualEnglish: the ONE decision about dual-line rendering, in one place so
   * views (Task 4 mounts every signing row through this) and this test agree.
   * Returns the English source to DISCLOSE, not a boolean, so the decision
   * and the panel share one lookup: a second I18n.enFor call could read a
   * different value and leave a line's panel disagreeing with the reason the
   * line was rendered dual-line.
   * @param {string} [key] dotted locale key; falsy for dynamic values
   *   (amounts, ids, symbols) which have no English source by construction.
   * @param {string} text the already-translated text about to be displayed.
   * @returns {string|null} the English reference to show, or null for the
   *   plain path — returned only when: the value is a real string, the key
   *   is a non-empty string, the key is not verified, the active locale is
   *   machine-filled, an English source exists, and that source differs from
   *   the text on screen. Never throws. */
  function dualEnglish(key, text) {
    if (typeof key !== "string" || !key) return null;
    if (typeof text !== "string" || !text) return null;
    if (isVerified(key)) return null;
    if (!activeMachine()) return null;
    var src = englishSource(key);
    return (src && src !== text) ? src : null;
  }

  /* setOpen: add/remove the open-state class on the wrapper.
   * @param {Element} host the div.i18n-risk wrapper.
   * @param {boolean} on desired state.
   * @returns {Element} host, mutated. Failure: no-op on a missing host. */
  function setOpen(host, on) {
    if (!host) return host;
    var names = String(host.className || "").split(/\s+/);
    var out = [], i;
    for (i = 0; i < names.length; i++) {
      if (names[i] && names[i] !== OPEN_CLASS) out.push(names[i]);
    }
    if (on) out.push(OPEN_CLASS);
    host.className = out.join(" ");
    return host;
  }

  /* panelIn: the English panel inside a dual-line wrapper. The wrapper's
   * children are flat and created here in a known order, so a direct-child
   * scan is exact and needs no selector engine; it also keeps the disclosure
   * working where querySelector is absent.
   * @param {any} host wrapper element (the button's parentNode).
   * @returns {any} the panel, or null when absent. Never throws. */
  function panelIn(host) {
    if (!host || !host.children) return null;
    var kids = host.children, i;
    for (i = 0; i < kids.length; i++) {
      if (kids[i] && kids[i].className === EN_CLASS) return kids[i];
    }
    return null;
  }

  /* toggle: flip one line's disclosure.
   * @param {any} btn the matched asterisk button (EventDelegate's second arg).
   * @returns {boolean} true when a panel was toggled. Failure: false (and no
   *   DOM change) when the button has no wrapper or the wrapper has no panel. */
  function toggle(btn) {
    if (!btn) return false;
    var host = btn.parentNode;
    var panel = panelIn(host);
    if (!panel) return false;
    var open = btn.getAttribute && btn.getAttribute("aria-expanded") === "true";
    if (btn.setAttribute) btn.setAttribute("aria-expanded", open ? "false" : "true");
    panel.hidden = open;
    setOpen(host, !open);
    return true;
  }

  /* bindDisclosure: attach the ONE delegated click listener for the app.
   * Delegation (not a listener per row) keeps the cost flat on a signing
   * dialog that renders dozens of lines, and re-renders after a locale switch
   * keep working because the listener lives on document. Failure: never
   * throws — a missing delegate helper or a missing document just leaves the
   * asterisk visible but inert rather than taking the confirm dialog down. */
  function bindDisclosure() {
    if (bound) return;
    if (typeof EventDelegate === "undefined" || !EventDelegate || typeof EventDelegate.delegate !== "function") return;
    if (typeof document === "undefined" || !document) return;
    try {
      EventDelegate.delegate(document, "." + STAR_CLASS, "click", function (evt, matched) {
        toggle(matched);
      });
      bound = true;
    } catch (e) {
      /* Disclosure stays inert; the line still renders plain text + asterisk. */
    }
  }

  /* render: the string, dual-line when warranted, plain otherwise. Callers
   * append the result unconditionally — the answer is always an element,
   * never a bare string and never null (Task 4 mounts this with appendChild,
   * and appendChild(null) would insert the text "null").
   * @param {Document} doc owner document (callers pass theirs).
   * @param {string|number|null|undefined} text the already-translated text to
   *   display; non-strings are stringified, null/undefined render empty.
   * @param {string} [key] dotted locale key enabling the English reference.
   * @returns {HTMLElement} span.i18n-risk-plain or div.i18n-risk — never a
   *   bare string, so callers can append unconditionally. Never throws. */
  function render(doc, text, key) {
    var str = (text === undefined || text === null) ? "" : String(text);
    var owner = (doc && typeof doc.createElement === "function") ? doc
      : ((typeof document !== "undefined" && document && typeof document.createElement === "function") ? document : null);
    if (!owner) return degraded();
    var enText = dualEnglish(key, str);
    if (enText === null) return mk(owner, "span", str, "i18n-risk-plain");

    uid += 1;
    var enId = "i18n-risk-en-" + uid;
    var wrap = mk(owner, "div", null, WRAP_CLASS);
    wrap.appendChild(mk(owner, "span", str, "i18n-risk-native"));

    var star = mk(owner, "button", "*", STAR_CLASS);
    star.type = "button";
    star.setAttribute("aria-expanded", "false");
    star.setAttribute("aria-controls", enId);
    star.setAttribute("aria-label", SHOW_EN_LABEL);
    if (typeof touchable === "function") touchable(star);
    wrap.appendChild(star);

    /* enText is the SAME string the decision compared against — one lookup. */
    var en = mk(owner, "div", enText, EN_CLASS);
    en.id = enId;
    en.hidden = true;
    wrap.appendChild(en);

    /* The link sits on the wrapper, not inside the panel, so the English
     * reference stays byte-for-byte the en master string with nothing appended
     * to it. CSS (.i18n-risk.is-open .i18n-risk-more) keeps it out of sight
     * until the line is open — which is why toggle() owns that class. */
    var more = mk(owner, "a", ABOUT_LABEL, "i18n-risk-more");
    more.href = ARTICLE;
    wrap.appendChild(more);

    bindDisclosure();
    return wrap;
  }

  /* isActive: is the honesty surface live at all? Views use it to decide
   * whether a legend or a page-level caveat is worth rendering at all.
   * @returns {boolean} true only on a machine-filled active locale. */
  function isActive() {
    return activeMachine();
  }

  return { render: render, wrap: render, isActive: isActive };
}());

if (typeof window !== "undefined") window.RiskText = RiskText;