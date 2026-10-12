/* ui/i18n-badge.js — the one PERSISTENT honesty signal: a collapsed chip in
 * the header that exists only while the active dictionary is machine-filled
 * and unverified (plan Task 5, spec §4.3). Every other surface in this
 * project is per-line (RiskText's asterisk) or per-dialog; this one answers
 * "what language am I reading?" once, for the whole app.
 * Owns: mount()/refresh()/visible(), the chip + note markup, and the
 *   collapsed<->expanded toggle.
 * Consumes: I18n.locale()/isMachineLocale(code)/t() (the SAME single
 *   condition RiskText reads — one rule, one answer, two surfaces), the
 *   shared DOM helpers (DOM.el/clear/append), the bare touchable() global
 *   (44px floor) and EventDelegate (ONE delegated listener, never a private
 *   binder). Every user-visible string is a keyed t() call.
 * Side effects: replaces the contents of the host slot on every mount, and
 *   adds at most one delegated "click" listener on the owner document, the
 *   first time a chip renders. NO storage, no network, no signing.
 * Created by: building-vanilla-slices skill,
 *   docs/superpowers/plans/2026-10-12-i18n-machine-translation.md Task 5.
 * Mirrors the extension shield-badge precedent (docs/vanilla-ui-dialog.md §2):
 *   "badge renders only when protected; in-browser users pay zero pixels.
 *   44px touch target, no hover-dependent behavior" — hidden means NO ELEMENT
 *   in the DOM, not a hidden one, so English and human-reviewed locales pay
 *   no layout box, no tab stop and no screen-reader announcement.
 * Failures: never throws. A missing/partial/throwing I18n, a missing DOM
 *   helper, a missing document and a missing slot all degrade to silence or
 *   to a chip built from raw platform calls — never a false warning, and
 *   never an exception out of the header.
 *
 * Two honesty rules this file exists to enforce, worth keeping if it is ever
 * rewritten:
 *   1. The chip is NOT dismissible. The note collapses on a tap and that is
 *      all: no localStorage, no sessionStorage, no "seen it" flag. A warning
 *      the user can lose is not a warning. The chip is always still there
 *      after the note closes.
 *   2. The badge must not appear on an error path. isMachineLocale() answers
 *      false for en, for an unloaded dict and for an unknown code
 *      (i18n.js:95-109), so a dictionary we cannot read can never raise a
 *      complaint about itself. Every guard below is written to fail CLOSED.
 */
var I18nBadge = (function () {
  "use strict";

  /* Where the note's two promises lead. The article lands with the next task
   * in this plan; until then the link is a dead route (honest, not hidden). */
  var ARTICLE = "#/help/translation-limitations";
  var ISSUES = "https://github.com/litepresence/bitshares-vanilla-ui/issues/new?labels=translation";

  var CHIP_CLASS = "i18n-badge";
  var NOTE_CLASS = "i18n-badge-note";

  var host = null;      /* the header slot, or null before mount() */
  var ownerDoc = null;  /* document the delegated listener hangs off */
  var shown = false;    /* the visible() answer */
  var bound = false;    /* one delegated listener, however many chips */
  var uid = 0;          /* panel-id counter (ids must never collide) */

  /* t: keyed string with the English default kept verbatim at the call site.
   * Same guard shape as every other module in vanilla/js: an i18n.js that
   * failed to load leaves the English default rather than a blank chip.
   * @param {string} key dotted locale key.
   * @param {string} dflt English text, byte-identical to en.json.
   * @returns {string} never blank, never throws. */
  function t(key, dflt) {
    try {
      if (typeof I18n !== "undefined" && I18n && typeof I18n.t === "function") return I18n.t(key, dflt);
    } catch (e) { /* default below */ }
    return dflt;
  }

  /* activeMachine: is the ACTIVE locale machine-filled and unverified?
   * The one condition, identical to ui/risk-text.js activeMachine() — the
   * chip and the per-line asterisks can never disagree about what "machine"
   * means. isMachineLocale() takes the CODE (i18n.js:107); calling it bare
   * answers "not machine" for every locale, so the code comes from
   * locale(). Fails CLOSED: false when I18n is absent, incomplete or throws.
   * @returns {boolean} true only on a loaded, machine-filled, non-en dict. */
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

  /* mk: ONE element through the SHARED DOM helper — never reimplemented here.
   * Falls back to the raw owner.createElement only when the DOM global is
   * absent (a page that did not load utils/dom.js), the same guard shape
   * ui/confirm.js and ui/risk-text.js use, so a missing helper degrades the
   * chip instead of throwing a ReferenceError out of the header.
   * @param {Document} owner owner document (createElement known good).
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

  /* floor: apply the 44px touch floor when the shared helper is loaded.
   * @param {any} el element to floor (may be null).
   * @returns {any} the same element, possibly style-mutated. Never throws. */
  function floor(el) {
    if (el && typeof touchable === "function") touchable(el);
    return el;
  }

  /* place/clearHost: the shared DOM.append/DOM.clear when they are loaded,
   * the platform calls when they are not (same guard shape as above).
   * @returns {void} never throws. */
  function clearHost(node) {
    if (!node) return;
    if (typeof DOM !== "undefined" && DOM && typeof DOM.clear === "function") {
      DOM.clear(node);
      return;
    }
    while (node.firstChild) node.removeChild(node.firstChild);
    if (node.children) node.children.length = 0;
  }

  /* place: append both children of the slot in one call.
   * @returns {void} never throws. */
  function place(node, chip, note) {
    if (!node) return;
    if (typeof DOM !== "undefined" && DOM && typeof DOM.append === "function") {
      DOM.append(node, chip, note);
      return;
    }
    node.appendChild(chip);
    node.appendChild(note);
  }

  /* noteIn: the panel that belongs to one chip. The slot's children are flat
   * and created in a known order here, so a direct-child scan is exact and
   * needs no selector engine (and no getElementById, which a minimal page
   * or a Node harness may not have).
   * @param {any} slot the chip's parentNode.
   * @returns {any} the note element, or null when absent. Never throws. */
  function noteIn(slot) {
    if (!slot || !slot.children) return null;
    var kids = slot.children, i;
    for (i = 0; i < kids.length; i++) {
      if (kids[i] && kids[i].className === NOTE_CLASS) return kids[i];
    }
    return null;
  }

  /* toggle: flip one chip's disclosure. The state is the chip's own
   * aria-expanded plus the note's hidden — no module-level flag and no class
   * — so it cannot drift out of sync with what assistive tech is told, a
   * repaint cannot lose it, and two chips can never drive each other.
   * @param {any} btn the matched chip (EventDelegate's second argument).
   * @returns {boolean} true when a panel was toggled. Failure: false, and no
   *   DOM change, when the chip has no slot or the slot has no panel. */
  function toggle(btn) {
    if (!btn) return false;
    var note = noteIn(btn.parentNode);
    if (!note) return false;
    var open = btn.getAttribute && btn.getAttribute("aria-expanded") === "true";
    if (btn.setAttribute) btn.setAttribute("aria-expanded", open ? "false" : "true");
    note.hidden = open;
    return true;
  }

  /* bindToggle: attach the ONE delegated click listener for the app.
   * Delegation (not a listener per chip) keeps the cost at one handler
   * however many times the chip is rebuilt on locale switches, and a chip
   * painted AFTER the listener exists still answers. Failure: never throws —
   * a missing delegate helper or a missing document leaves the chip visible
   * but inert (the note is still in the DOM, so nothing is lost silently). */
  function bindToggle(doc) {
    if (bound || !doc) return;
    if (typeof EventDelegate === "undefined" || !EventDelegate || typeof EventDelegate.delegate !== "function") return;
    try {
      EventDelegate.delegate(doc, "." + CHIP_CLASS, "click", function (evt, matched) {
        toggle(matched);
      });
      bound = true;
    } catch (e) {
      /* Disclosure stays inert; the chip still says which language it is. */
    }
  }

  /* buildNote: the expanded explanation — the warning sentence and the two
   * routes the warning promises (why this is machine text, and how to fix
   * it). Built as a sibling of the chip so the chip itself stays ONE 44px
   * target and the note is the only thing that appears on expansion.
   * @param {Document} doc owner document.
   * @param {string} noteId id to stamp (from the chip's aria-controls).
   * @returns {HTMLElement} detached, hidden note. Never throws. */
  function buildNote(doc, noteId) {
    var note = mk(doc, "div", null, NOTE_CLASS);
    note.id = noteId;
    note.setAttribute("role", "note");
    note.setAttribute("aria-live", "polite");
    note.hidden = true;

    note.appendChild(mk(doc, "p", t("i18n.badge_body",
      "These translations were written by a machine and have not been checked by a human. Lines marked * on the signing screens also show the original English."),
      "i18n-badge-text"));

    var links = mk(doc, "p", null, "i18n-badge-links");
    var more = mk(doc, "a", t("i18n.badge_details", "What this means"), "i18n-badge-link");
    more.href = ARTICLE;
    floor(more);
    var improve = mk(doc, "a", t("i18n.badge_improve", "Help improve this translation"), "i18n-badge-link");
    improve.href = ISSUES;
    improve.target = "_blank";
    improve.rel = "noopener noreferrer";
    floor(improve);
    links.appendChild(more);
    links.appendChild(improve);
    note.appendChild(links);
    return note;
  }

  /* refresh: re-decide visibility for the ACTIVE locale and rebuild the slot.
   * Called on boot, on every locale switch (App.localizeShell -> paintI18nBadge)
   * and whenever the header is repainted. Rebuilding (rather than hiding)
   * is what makes "hidden" mean "no element at all".
   * @returns {void} never throws; on any failure the slot ends up empty,
   *   which is the zero-pixel state every honest path agrees on. */
  function refresh() {
    if (!host) return;
    var doc = ownerDoc || host.ownerDocument ||
      (typeof document !== "undefined" ? document : null);
    if (!doc || typeof doc.createElement !== "function") return;
    try {
      clearHost(host);
      if (!activeMachine()) { shown = false; return; }
      uid += 1;
      var noteId = "i18n-badge-note-" + uid;
      var chip = mk(doc, "button", t("i18n.badge_chip", "i18n"), CHIP_CLASS);
      chip.type = "button";
      chip.setAttribute("aria-expanded", "false");
      chip.setAttribute("aria-controls", noteId);
      chip.setAttribute("aria-label", t("i18n.badge_label",
        "Translation status: machine translated, not human verified"));
      floor(chip);
      var note = buildNote(doc, noteId);
      bindToggle(doc);
      place(host, chip, note);
      shown = true;
    } catch (e) {
      clearHost(host);
      shown = false;
    }
  }

  /* mount: bind the slot (once) and paint for the current locale. Called by
   * App.paintI18nBadge on every shell repaint, so passing the same slot again
   * is the normal case, not an error.
   * @param {Document} doc owner document (the shared delegate listener hangs
   *   off it, so the chip answers clicks without a per-chip binder).
   * @param {Element|null|undefined} hostEl the header slot from index.html.
   * @returns {void} never throws; a falsy slot leaves the previous state. */
  function mount(doc, hostEl) {
    if (!hostEl) return;
    host = hostEl;
    if (doc && typeof doc.createElement === "function") ownerDoc = doc;
    refresh();
  }

  /* visible: is the chip mounted right now? False for English, human-reviewed
   * and unreadable locales — which IS the zero-pixel promise, and what a
   * caller (or a test) asserts instead of reading the DOM.
   * @returns {boolean} */
  function visible() { return shown === true; }

  return { mount: mount, refresh: refresh, visible: visible };
}());

if (typeof window !== "undefined") window.I18nBadge = I18nBadge;
if (typeof module !== "undefined") module.exports = I18nBadge;