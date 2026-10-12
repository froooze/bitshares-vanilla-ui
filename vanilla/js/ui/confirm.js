/* ui/confirm.js — shared transaction-confirm builder.
 * Owns: div.confirm-dialog (h3 title + dl.confirm named rows + fee line +
 *   opt-in details.raw drill-down + div.confirm-actions holding Back
 *   (btn-ghost) + Sign & Send buttons;
 *   Esc routes to onBack; returns the container for the caller to mount).
 *   Also owns the ONE place a signing line reaches the honesty surface: the
 *   title and every row term mount through RiskText, so a machine-filled
 *   locale shows the English master beside a string the user is about to
 *   sign. Dual-line vs plain stays RiskText's single decision, never ours.
 * Consumes: DOM global (el/append — never reimplemented here; raw
 *   createElement fallback only when DOM is absent, e.g. Node without the
 *   shim), touchable() global for the 44px touch floor (guarded: skipped
 *   when absent, e.g. Node), RiskText global for keyed lines (guarded the
 *   same way: a page that did not load it degrades to plain text).
 * Side effects: creates DOM elements only; adds one doc-level keydown
 *   listener per show() (removed on Back/Send/Esc — never leaks across
 *   confirms). No storage, no network, no signing — the caller owns
 *   publish (buildTx + fresh-WIF sendAndProve + head-marked result).
 * Origin: Task 3.1 of docs/superpowers/plans/2026-10-04-shared-utilities-refactor.md;
 *   common subset of the locals in asset-ui.js (confirm ~line 185: named
 *   rows + fee + Back/Sign&Send), barter-ui.js (confirmPropose ~line 308:
 *   h3 + dl.confirm + Back btn-ghost), borrow-ui.js, credit-ui.js
 *   (confirmList/sendConfirm ~lines 160/232), htlc-ui.js, pool-ui.js
 *   (sendConfirm ~line 234), proposal-ui.js (confirmList/sendConfirm
 *   ~lines 145/237): title/rows/fee/Back/Send only. Unlock gates, status
 *   lines, and sendAndProve stay in the calling views.
 * No deps, ES5, works on file:// and http:// (classic script tag). */
var ConfirmDialog = (function () {
  /* Resolve the shared DOM helper without capturing it (script order in
   * index.html guarantees window.DOM exists before this file runs).
   * @return {object|null} DOM global or null when absent (Node without shim).
   * Failure: returns null — show() falls back to raw doc.createElement. */
  function dom() {
    if (typeof DOM !== "undefined" && DOM) return DOM;
    return null;
  }

  /* Apply the 44px touch floor when the helper exists.
   * @param {HTMLElement} el element to floor (may be null).
   * @return {HTMLElement} same element, possibly style-mutated.
   * Failure: no-op when touchable is absent (Node tests, minimal pages). */
  function floor(el) {
    if (el && typeof touchable === "function") touchable(el);
    return el;
  }

  /* Resolve the owner document: explicit cfg.doc first (Node tests), then
   * the browser global. Callers on real pages pass nothing — document wins.
   * @param {any} cfg show() config bag (may carry .doc).
   * @return {Document|null} usable document or null.
   * Failure: returns null when neither exists (show() throws honestly). */
  function docOf(cfg) {
    if (cfg && cfg.doc && typeof cfg.doc.createElement === "function") return cfg.doc;
    if (typeof document !== "undefined" && document) return document;
    return null;
  }

  /* Build one element via the shared helper, or raw when DOM is absent.
   * @param {Document} doc owner document.
   * @param {string} tag tag name.
   * @param {string|null} text textContent (null leaves it empty).
   * @param {string} cls optional className.
   * @return {HTMLElement} new detached element.
   * Failure: text null/undefined renders as empty text (never "null"). */
  function mk(doc, tag, text, cls) {
    var D = dom();
    var el;
    if (D) return D.el(doc, tag, text, cls);
    el = doc.createElement(tag);
    if (text !== undefined && text !== null) el.textContent = text;
    if (cls) el.className = cls;
    return el;
  }

/* risk: ONE signing line, rendered by the shared honesty surface
   * (ui/risk-text.js) so a machine-filled locale can disclose the English
   * master beside it. NEVER reimplemented here — "is this line high-risk?"
   * is RiskText's single decision, and re-deciding it here is how two
   * surfaces would come to disagree about the same string.
   * @param {Document} doc owner document.
   * @param {any} text the already-translated string about to be shown.
   * @param {any} key dotted locale key, or falsy for a dynamic value
   *   (amounts, asset symbols, object ids, dates — locale-independent by
   *   §3.5 and deliberately never wrapped).
   * @return {any} an element holding the line. Failure: never throws — a
   *   missing, unusable or throwing RiskText degrades to a plain span
   *   carrying the same text, because a signing dialog must never be taken
   *   down by the honesty surface that decorates it. */
  function risk(doc, text, key) {
    var node = null;
    try {
      if (typeof RiskText !== "undefined" && RiskText && typeof RiskText.render === "function") {
        node = /** @type {any} */ (RiskText.render(doc, text, key || null));
      }
    } catch (e) { node = null; }
    if (node && typeof node === "object") return node;
    return mk(doc, "span", text);
  }

  /* line: one SEMANTIC slot (the h3 heading, or a row's dt) whose CONTENT is
   * a RiskText line. The host is built EMPTY and the widget mounted inside
   * it, deliberately: RiskText answers a <span> on the plain path and a
   * <div> on the dual path, so substituting it for the host would demote the
   * dialog heading to a span and un-pair every <dl> dt/dd — a screen-reader
   * regression on the one dialog a user reads before signing. Nesting keeps
   * the markup a real dialog and still gives the line its disclosure.
   * @param {Document} doc owner document.
   * @param {string} tag host tag name (always a heading or description term).
   * @param {any} text text for the line (may be null/undefined → empty).
   * @param {any} key optional dotted locale key (see risk()).
   * @return {HTMLElement} the detached host, with the line inside it.
   * Failure: never throws (risk() degrades). */
  function line(doc, tag, text, key) {
    var host = mk(doc, tag, null);
    host.appendChild(risk(doc, text, key));
    return host;
  }

  /* Render the confirm subset: heading, named rows, fee line, Back + Send.
   * @param {any} cfg {title: string, titleKey?: string (dotted locale key
   *   for the title — OPTIONAL; absent renders the title exactly as before,
   *   so the ~16 existing call sites work untouched until they opt in),
   *   rows: [[term, text, rawTitle?, termKey?]...]
   *   (third element sets dd.title = raw, e.g. "raw 123" or "12345";
   *   FOURTH element is the term's dotted locale key — same opt-in rule:
   *   absent renders plain. Key a STATIC label only; amounts, asset
   *   symbols, object ids and dates are locale-independent by §3.5 and
   *   must never carry a key),
   *   feeHuman: string (human fee line; skipped when null/undefined),
   *   feeTerm?: string (caller's already-keyed fee dt, e.g.
   *   t("borrow.fee", "Fee"); fallback "Fee" when absent),
   *   feeRawTitle?: string|null (raw fee integer for the fee dd title,
   *   principle #6: human terms with raw in title; no title when absent),
   *   onBack: function, onSend: function,
   *   rawJson?: string|null (pre-stringified op JSON for the raw drill-down),
   *   rawObj?: any (alternative: stringified here in try/catch — rawJson wins;
   *   unstringifiable values fail closed to no drill-down),
   *   rawLabel?: string (summary text; fallback the literal "Raw JSON" —
   *   callers SHOULD pass a keyed label, e.g. confirm.op_json_label),
   *   doc?: Document (Node-test seam; browsers omit it),
   *   backLabel?: string (default "Back"), sendLabel?: string
   *   (default "Sign & Send") — translated labels ride in from the caller
   *   so this module carries no locale machinery.}
   * @return {HTMLElement} div.confirm-dialog (caller appends it; the
   *   returned node stays usable after Back/Send fire).
   * Failure: throws Error("confirm: no document") with no document;
   *   null/undefined rows render as an empty list (never throws). */
  function show(cfg) {
    cfg = cfg || {};
    var D = dom();
    var doc = docOf(cfg);
    var title = (cfg.title === undefined || cfg.title === null) ? "" : cfg.title;
    var rows = cfg.rows || [];
    var onBack = (typeof cfg.onBack === "function") ? cfg.onBack : function () {};
    var onSend = (typeof cfg.onSend === "function") ? cfg.onSend : function () {};
    var backLabel = (cfg.backLabel === undefined || cfg.backLabel === null) ? "Back" : cfg.backLabel;
    var sendLabel = (cfg.sendLabel === undefined || cfg.sendLabel === null) ? "Sign & Send" : cfg.sendLabel;
    var feeTerm = (cfg.feeTerm === undefined || cfg.feeTerm === null) ? "Fee" : cfg.feeTerm;
    var box;
    var list;
    var actions;
    var back;
    var send;
    var dd;
    var i;
    if (!doc) throw new Error("confirm: no document");
    box = mk(doc, "div", null, "confirm-dialog");
    box.appendChild(line(doc, "h3", title, cfg.titleKey));
    list = mk(doc, "dl", null, "confirm");
    for (i = 0; i < rows.length; i++) {
      list.appendChild(line(doc, "dt", rows[i][0], rows[i][3]));
      dd = mk(doc, "dd", rows[i][1]);
      if (rows[i][2]) dd.title = rows[i][2];
      list.appendChild(dd);
    }
    if (cfg.feeHuman !== undefined && cfg.feeHuman !== null) {
      list.appendChild(mk(doc, "dt", feeTerm));
      dd = mk(doc, "dd", cfg.feeHuman);
      if (cfg.feeRawTitle) dd.title = cfg.feeRawTitle;
      list.appendChild(dd);
    }
    if (D) D.append(box, list);
    else box.appendChild(list);
    actions = mk(doc, "div", null, "confirm-actions");
    back = floor(mk(doc, "button", backLabel, "btn-ghost"));
    back.type = "button";
    send = floor(mk(doc, "button", sendLabel));
    send.type = "button";
    if (D) D.append(actions, back, send);
    else { actions.appendChild(back); actions.appendChild(send); }
    /* Raw drill-down (opt-in, TransactionConfirm view-qr/JSON concept +
     * transfer-confirm op-JSON precedent): op JSON behind a <details
     * class="raw"> (app.css skin, phone-safe) BEFORE the actions so the
     * order reads review → raw → buttons. textContent only, never secrets
     * (unsigned ops carry no keys). rawJson (pre-stringified) wins; else
     * rawObj stringifies here in try/catch — unstringifiable values fail
     * closed to no drill-down. Skipped when neither yields text. */
    var rawText = "";
    if (typeof cfg.rawJson === "string" && cfg.rawJson) {
      rawText = cfg.rawJson;
    } else if (cfg.rawObj !== undefined && cfg.rawObj !== null) {
      try { rawText = JSON.stringify(cfg.rawObj, null, 2) || ""; } catch (e) { rawText = ""; }
    }
    if (rawText) {
      var rawDet = mk(doc, "details", null, "raw");
      var rawLabel = (cfg.rawLabel === undefined || cfg.rawLabel === null) ? "Raw JSON" : cfg.rawLabel;
      var rawSum = mk(doc, "summary", rawLabel);
      try { rawSum.setAttribute("aria-label", rawLabel); } catch (e) { /* text stands */ }
      if (D) D.append(rawDet, rawSum);
      else rawDet.appendChild(rawSum);
      var rawPre = mk(doc, "pre", rawText);
      if (D) D.append(rawDet, rawPre);
      else rawDet.appendChild(rawPre);
      try {
        if (typeof box.insertBefore === "function") box.insertBefore(rawDet, actions);
        else box.appendChild(rawDet);
      } catch (e) {
        try { box.appendChild(rawDet); } catch (e2) { /* review stands */ }
      }
    }
    if (D) D.append(box, actions);
    else box.appendChild(actions);

    /* Focus capture + return (listener/focus lifecycle): record the opener,
     * focus the first (Back) button, restore the opener on every close path
     * (Back/Send/Esc). All guarded — fake docs without activeElement/focus
     * degrade to the prior tab order. */
    var opener = null;
    try { opener = (doc.activeElement && typeof doc.activeElement.focus === "function") ? doc.activeElement : null; } catch (e) { opener = null; }
    function restoreFocus() {
      try { if (opener && typeof opener.focus === "function") opener.focus(); } catch (e) { /* tab order stands */ }
    }
    /* One-shot Esc: Back exactly once, then detach (repeat Esc presses
     * after resolve are no-ops — the listener is gone). */
    function cleanup() {
      try {
        if (doc.removeEventListener) doc.removeEventListener("keydown", onKey);
      } catch (e) { /* listener is best-effort in minimal docs */ }
    }
    function onKey(e) {
      e = e || {};
      if (e.key === "Escape" || e.keyCode === 27) {
        cleanup();
        restoreFocus();
        onBack();
      }
    }
    try {
      if (doc.addEventListener) doc.addEventListener("keydown", onKey);
    } catch (e) { /* confirm still works via the buttons */ }
    back.addEventListener("click", function () { cleanup(); restoreFocus(); onBack(); });
    send.addEventListener("click", function () { cleanup(); restoreFocus(); onSend(); });
    try { if (typeof back.focus === "function") back.focus(); } catch (e) { /* tab order stands */ }
    return box;
  }

  return {
    show: show
  };
})();

if (typeof window !== "undefined") /** @type {any} */ (window).ConfirmDialog = ConfirmDialog;
if (typeof module !== "undefined") module.exports = ConfirmDialog;
